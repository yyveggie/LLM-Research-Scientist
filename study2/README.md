# Study 2：GPT 作为 Research Ethicist

本指南面向希望复现 Lehr et al. 2024 Study 2 方法流程的使用者。

Study 2 测试模型是否能像研究伦理/方法顾问一样，发现研究方案中的不良研究实践，并提出改善建议。


## 输入

输入来自作者公开材料：

```text
materials_txt/Research Materials/GPT as Research Ethicist Materials 20240227.txt
```

生成或刷新输入文件：

```bash
python3 study2/prepare_inputs.py
```

生成内容包括：

- `bad_initial_prompts.csv`：18 个 bad research initial prompts
- `good_initial_prompt.csv`：good research 补充研究使用的统一 initial prompt
- `bad_research_vignettes.csv`：6 个 bad research vignettes
- `good_research_vignettes.csv`：2 个 good research vignettes
- `rubrics.csv`：各 vignette 对应的人工评分 rubric
- `study2_materials.json`：完整结构化材料

## 作者 Study 2 设计

Bad research 主研究：

- 18 个 initial prompts
- 6 个 bad research vignettes
  - `1a`、`2a`、`3a`：blatant bad research
  - `1b`、`2b`、`3b`：subtle bad research
- 每个模型共 `18 × 6 = 108` 个 responses

Good research 补充研究：

- 2 个 good research vignettes
- 使用一个统一 initial prompt

## LLM API 配置

运行器使用 OpenAI-compatible 的 chat-completions API，默认从全局配置文件读取模型提供商：

```text
model_providers.yaml
```

正式运行前，先在该文件中填写 `base_url`、`api_key`、`model`、`max_concurrency` 和 `timeout`。如果文件中有多个提供商，可用 `--provider` 选择其中一个。

## Dry run 测试

```bash
python3 study2/run_study2.py --dry-run --limit 1
```

## 运行 bad research 主研究

```bash
python3 study2/run_study2.py --sleep 1
```

默认流程是两轮对话：

1. 发送 initial prompt。
2. 记录模型回应。
3. 在同一对话中发送 vignette。
4. 保存模型对 vignette 的最终反馈。

这符合作者材料中“initial prompt 先给出，然后复制 bad research vignette”的流程。

正式方法复现不要使用 `--single-turn`。该选项仅用于流程检查，因为作者方法是先发 initial prompt，再在同一对话中复制 vignette。

## 运行 good research 补充研究

```bash
python3 study2/run_study2.py --good --sleep 1
```

## 原始输出格式

模型原始响应保存为 JSONL：

```text
study2/outputs/raw_model_responses/study2_research_ethicist.jsonl
```

每一行包含：

- `timestamp_utc`
- `study`
- `provider`
- `model`
- `base_url`
- `timeout`
- `max_concurrency`
- `condition`
- `conversation_mode`
- `prompt_id`
- `prompt_source`
- `vignette_id`
- `rubric_id`
- `initial_prompt`
- `vignette`
- `initial_response`
- `final_response`
- `initial_raw`
- `final_raw`

其中 `final_response` 是需要人工评分的主要文本。

## 人工评分

使用：

```text
study2/audit/response_scoring_template.csv
```

每个 response 对应 CSV 中一行。

评分字段：

- `q1` 到 `q10`：对应该 vignette 的 10 个 rubric items
- `rubric_id`：用于选择对应作者 rubric
- `total_score`：总分
- `coder`：评分人
- `notes`：备注

每个 response 最多 10 分。通常每个 rubric item 填 `1` 或 `0`：模型明确指出该问题或给出相应建议则为 `1`，否则为 `0`。如果复现者希望使用 `0.5` 等部分得分，需要在正式编码前预先决定评分规则，并在复现报告中说明。

Bad research 的 rubric 映射为：`1a` 与 `1b` 共用 `1a-b`，`2a` 与 `2b` 共用 `2a-b`，`3a` 与 `3b` 共用 `3a-b`；good research 使用 `1c` 或 `2c`。Good research 补充研究不是让模型找错误，而是评估模型是否错误批评良好研究，或是否能识别良好实践。

原作者使用人工 coder 对模型回答评分。因此本复刻保留人工评分环节，不用 LLM 自动代替人工评分。