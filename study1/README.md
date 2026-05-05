# Study 1：GPT 作为 Research Librarian

本指南面向希望复现 Lehr et al. 2024 Study 1 方法流程的使用者。

复现目标是：使用作者原始自然语言文献检索 prompt，让复现者配置的任意 LLM API 执行同样任务。文献真实性、幻觉、完整性、相关性和引用量等判断，应按照原作者方法保留为人工审核环节。

## 输入

输入来自作者公开材料：

```text
materials_txt/Research Materials/GPT as Research Librarian Materials 20240227.txt
```

共有 25 个主题，分为 5 个主题宽度等级：

- Broad
- Somewhat Broad
- Moderate
- Somewhat Narrow
- Narrow

每个主题包含：

- `breadth`
- `breadth_level`
- `topic`
- `initial_prompt`
- `followup_template`

生成或刷新输入文件：

```bash
python3 study1/prepare_inputs.py
```

生成文件位置：

```text
study1/inputs/study1_topics_and_prompts.json
study1/inputs/study1_topics_and_prompts.csv
```

## LLM API 配置

运行器使用 OpenAI-compatible 的 chat-completions API，默认从全局配置文件读取模型提供商：

```text
model_providers.yaml
```

正式运行前，先在该文件中填写 `base_url`、`api_key`、`model`、`max_concurrency` 和 `timeout`。如果文件中有多个提供商，可用 `--provider` 选择其中一个。

## Dry run 测试

Dry run 不会调用 API，只会检查流程并写出空响应记录。

```bash
python3 study1/run_study1.py --dry-run --limit 1 --max-followups 1
```

## 正式运行 Study 1

```bash
python3 study1/run_study1.py --sleep 1
```

流程如下：

1. 对某个主题发送作者原始 `initial_prompt`。
2. 统计模型给出了多少篇论文。
3. 如果少于 20 篇，并且模型没有明确承认无法找到文献，则发送 follow-up prompt。
4. follow-up prompt 中，`x` 替换为已给出的论文数，`y` 替换为 `20 - x`。
5. 重复，直到模型给出 20 篇 reference，或明确承认无法完成。

默认不设置固定 follow-up 次数上限，因为作者材料说明 follow-up 会重复到上述停止条件为止。若复现者只是在检查流程，或担心某些模型反复不给足 20 篇，可以临时加入 `--max-followups` 作为运行安全限制；该限制不属于作者方法本身。

## 人工计数模式

自动 reference 计数只是启发式估算。为了最忠实于作者流程，正式复现实验应使用人工计数模式：

```bash
python3 study1/run_study1.py --manual-count
```

每轮模型输出后，手动输入目前累计给出的论文数。如果模型已经明确承认找不到文献，输入 `d`。

如果不使用 `--manual-count`，脚本会根据编号或年份启发式估算 reference 数量。这适合 dry run 或流程检查，但不应作为正式方法复现的首选。

## 原始输出格式

模型原始响应保存为 JSONL：

```text
study1/outputs/raw_model_responses/study1_research_librarian.jsonl
```

每一行包含：

- `timestamp_utc`
- `study`
- `provider`
- `model`
- `base_url`
- `timeout`
- `max_concurrency`
- `topic`
- `breadth`
- `breadth_level`
- `turn`
- `prompt`
- `response`
- `estimated_count`
- `acknowledged_defeat`
- `raw`

其中 `response` 字段是需要人工审核的模型原始文本。

## 人工审核

使用以下文件：

```text
study1/audit/reference_coding_template.csv
```

人工审核时，每一条 reference 对应 CSV 中一行。

核心编码变量与作者 codebook 对齐：

- correctness
- hallucination
- error
- completeness
- relevance
- acknowledged fiction
- admitted no citation found
- citation counts

编码单位是模型生成的单条 reference。每个主题目标是 20 条 references；如果使用 follow-up，后续响应仍属于同一个主题对话，应与初始响应合并并按顺序编码。

`correctness` 按作者 codebook 区分：

- `Correct`：真实论文，且 citation 基本准确。
- `Hallucination`：完全虚构，或严重到无法验证为真实论文。
- `Error`：论文真实存在，但年份、期刊、卷号、页码等书目信息有小错误。

`relevance` 与 `correctness` 分开编码：真实论文也可能与主题不相关。citation count 建议由两名 coder 或两个来源分别记录，再计算平均值。
