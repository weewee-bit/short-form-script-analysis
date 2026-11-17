# 分析清单与输出规范

## 逐条与逐句

- **原始稿和校对稿**：保存说话者、句段时间、原始识别文本、校对文本和修改依据。标记听不清、口语语气词、重复和可靠停顿。对照内嵌字幕时记差异所属句与画面时间。
- **节拍和信息流**：根据实际功能分段。常见节拍包括问题、背景、证据、解释、演示、结果和 CTA。每段写原文或句段 ID、起止、主要信息、回应与引出的观众问题、承接和删去的影响。分清核心信息、必要背景、证据和重复。
- **开头与 Open Loops**：分开解释首句、前三秒和整个开头。按 Attention、Relevance、Expectation 指出起效的具体措辞，检查明确利益、信息差、情绪、跳步、夸大和首秒铺垫。每个实质性悬念记录开环、等待期间新增信息、承诺答案、正文兑现点和兑现不足。只在外部链接、群聊或评论提供的部分标明交付位置。
- **逐句审计**：每行一个句子或明确标作近似的语义单元。字段含视频 ID、句子 ID、原文、起止时间、节拍、句子功能、新信息、观众问题、心理机制、与前后连接、证据状态、重要性、潜在问题和待复核事项。重要性用 ESSENTIAL、SUPPORTING、OPTIONAL 或 REDUNDANT。解释这句话为何在此位置。理由不明确时标待评估。
- **语言、解释与价值**：检查句长、密度、口语、术语、转折、对比、数字、情绪词和动词，选能解释观众理解和记忆的例子。分析先给结果、类比、输入输出、操作步骤、必要条件及限制。记录谁得到什么，以及正文何时首次交付可用信息。由文本推断的心理反应标为可能的效果。
- **语言指纹**：区分通用技巧、单条特征和跨作品习惯。比较开头、转折、论证、强调、称呼和收尾。样本计数附分母和匹配定义。可复用模式写原例、原理、适用场景、前提和误用。
- **事实核查**：每条记录原话或时间、可验证命题、来源、日期和结论。状态用 VERIFIED、PARTIALLY SUPPORTED、UNVERIFIED、MISLEADING、OUTDATED、OPINION 或 PREDICTION。把来源证实的范围写到该行。拆开发布时间、功能、版本、价格、性能、地区、样本等不同口径。证据不足保留核查缺口。
- **评分**：Hook Clarity、Audience Relevance、Narrative Coherence、Information Value、Explanation Quality、Credibility、Payoff Quality 各 1–5。1 表示严重不足，3 表示部分做到，5 表示在现有证据下充分。每项注明证据、扣分及不确定性。

## 完整文件交付

在用户指定位置或可交付的工作目录创建 `script_analysis/`。按实际覆盖输出以下文件。一次简短的文本拆解可以直接在对话交付。

| 文件 | 内容 |
|---|---|
| `transcript_verbatim.md`、`transcript_clean.md`、`transcript_timed.json` | 各条原始稿、校对稿、时间轴与来源。无可靠时间时省略时间轴文件，或保留用户要求的空时间字段。 |
| `narrative_structure.md`、`hook_analysis.md`、`information_flow.md`、`open_loops.md` | 节拍、Hook、逐句信息推进、悬念兑现 |
| `language_and_pacing.md`、`explanation_methods.md`、`fact_check.md`、`audience_value.md` | 语言与节奏、解释机制、事实、受众价值 |
| `creator_voice_profile.md`、`sentence_audit.csv`、`script_scorecard.md`、`reusable_patterns.md` | 风格、逐句审计、七项评分、写作机制 |
| `frame_script_alignment.csv.gz` | 获得媒体并请求帧级对齐时生成。记录每帧与字幕关系。 |
| `SCRIPT_ANALYSIS_REPORT.md` | 总报告和样本索引。链接各实际交付件。 |

总报告顺序为原始稿、核心结论、Hook、叙事、逐句与信息流、悬念、语言、解释、事实、风格、评分、可迁移机制、证据缺口。受众价值放在首次交付或 Hook 后。批量交付核对视频 ID、条数、片段时长、CSV 和 JSON 的引用，以及输出覆盖情况。
