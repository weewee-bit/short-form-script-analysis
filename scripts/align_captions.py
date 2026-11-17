#!/usr/bin/env python3
"""Create a cue JSON index and optionally align it to decoded video frames."""

import argparse
from bisect import bisect_left
from collections import defaultdict
import csv
from decimal import Decimal
import gzip
import json
from pathlib import Path
import re
import subprocess


TIMESTAMP = r"(?:[0-9]+:)?[0-5][0-9]:[0-5][0-9][.,][0-9]{3}"
CUE_TIMING = re.compile(
    rf"^\s*({TIMESTAMP})\s+-->\s+({TIMESTAMP})(?:\s+.*)?$"
)


def timestamp_us(stamp):
    clock, milliseconds = re.split("[.,]", stamp)
    seconds = 0
    for part in clock.split(":"):
        seconds = seconds * 60 + int(part)
    return (seconds * 1000 + int(milliseconds)) * 1000


def read_cues(path, video_id):
    contents = path.read_text(encoding="utf-8-sig").strip()
    cues = []
    for block in re.split(r"\n[ \t]*\n+", contents):
        lines = block.splitlines()
        if not lines:
            continue
        directive = lines[0].split(maxsplit=1)[0] if lines[0].strip() else ""
        if directive in {"WEBVTT", "NOTE", "STYLE", "REGION"}:
            continue
        timing_index = 0 if "-->" in lines[0] else 1
        if timing_index >= len(lines):
            continue
        timing_line = lines[timing_index]
        match = CUE_TIMING.fullmatch(timing_line)
        if match is None:
            if "-->" in timing_line:
                raise ValueError(f"Invalid cue timing in {path.name}: {timing_line}")
            continue
        start, end = map(timestamp_us, match.groups())
        if end <= start:
            raise ValueError(f"Cue end must follow its start in {path.name}: {timing_line}")
        original = "\n".join(lines[timing_index + 1:]).strip()
        if original:
            cues.append({
                "source_cue_id": lines[0].strip() if timing_index == 1 else None,
                "start_us": start,
                "end_us": end,
                "original_text": original,
            })
    if not cues:
        raise ValueError(f"No text cues found in {path.name}. Expected WebVTT or SRT.")
    cues.sort(key=lambda cue: cue["start_us"])
    for index, cue in enumerate(cues, 1):
        cue["cue_id"] = f"{video_id}-C{index:04d}"
    return cues


def seconds_to_us(value):
    return int(Decimal(value) * 1_000_000)


def read_frame_times(video):
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_format", "-show_entries",
        "frame=best_effort_timestamp_time:format=start_time", "-of", "json",
        str(video.resolve()),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as error:
        raise ValueError("FFprobe is required when --video is provided.") from error
    except subprocess.CalledProcessError as error:
        raise ValueError(f"FFprobe failed for {video.name}: {error.stderr.strip()}") from error

    media = json.loads(result.stdout)
    frames = media.get("frames", [])
    if not frames:
        raise ValueError(f"No video frames found in {video.name}.")
    timestamps = [frame.get("best_effort_timestamp_time") for frame in frames]
    if any(time in (None, "N/A") for time in timestamps):
        raise ValueError(f"Some frames in {video.name} lack a presentation timestamp.")
    timestamps = sorted(map(seconds_to_us, timestamps))
    start = media.get("format", {}).get("start_time")
    if start not in (None, "N/A"):
        origin, origin_source = seconds_to_us(start), "format_start_time"
    else:
        origin, origin_source = timestamps[0], "first_video_frame"
    return [time - origin for time in timestamps], origin, origin_source


def link_cues(cues, frame_times):
    starts, stops = defaultdict(list), defaultdict(list)
    for cue in cues:
        begin = bisect_left(frame_times, cue["start_us"])
        end = bisect_left(frame_times, cue["end_us"])
        cue["first_frame"] = begin if begin < end else None
        cue["last_frame"] = end - 1 if begin < end else None
        if begin < end:
            starts[begin].append(cue["cue_id"])
            stops[end].append(cue["cue_id"])
    return starts, stops


def write_frames(path, video_id, frame_times, starts, stops):
    with gzip.open(path, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("video_id", "frame_index", "pts_us", "active_cue_ids"))
        active = {}
        for number, pts in enumerate(frame_times):
            for cue_id in stops.get(number, ()):
                del active[cue_id]
            for cue_id in starts.get(number, ()):
                active[cue_id] = None
            writer.writerow((video_id, number, pts, "|".join(active)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captions", type=Path, help="UTF-8 WebVTT or SRT source")
    parser.add_argument("--video", type=Path, help="Local media for frame alignment")
    parser.add_argument("--video-id", default="V01")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.video_id):
        parser.error("--video-id must use letters, digits, hyphens or underscores.")
    try:
        cues = read_cues(args.captions, args.video_id)
        index = {
            "video_id": args.video_id,
            "captions_source": str(args.captions),
            "cue_interval": "start inclusive, end exclusive",
            "time_unit": "microsecond",
            "cues": cues,
        }
        if args.video:
            times, origin, origin_source = read_frame_times(args.video)
            starts, stops = link_cues(cues, times)
            index["video"] = {
                "source": str(args.video),
                "frame_count": len(times),
                "frame_index_base": 0,
                "absolute_origin_us": origin,
                "origin_source": origin_source,
            }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "captions_timed.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if args.video:
            write_frames(
                args.output_dir / "frame_script_alignment.csv.gz",
                args.video_id, times, starts, stops
            )
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
