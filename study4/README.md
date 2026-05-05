# Study 4：GPT 作为 Novel Data Predictor

本指南面向希望复现 Lehr et al. 2024 Study 4 方法流程的使用者。

Study 4 测试模型能否预测训练数据中不应包含的、后来才公开的跨国家 implicit / explicit attitudes 和 stereotypes。

## 文件夹结构

```text
study4/
  README.md
  prepare_inputs.py
  run_study4.py
  analyze_predictions.py
  inputs/
    study4_tasks.json
    study4_tasks.csv
    real_country_data.csv
    real_country_data_compact.csv
  outputs/
    raw_model_responses/
      study4_novel_data_predictor.jsonl
  audit/
    prediction_extraction_template.csv
```

## 输入来源

prompt 来源于作者公开材料：

```text
materials_txt/Research Materials/GPT as Novel Data Predictor Materials 20240227.txt
```

真实国家数据来源于作者公开 Excel：

```text
【data and code】chatgpt-as-research-scientist-probing-gpt-s-capabilities-as-a-research-librarian-research-ethicist-data/Data and Codebooks/GPT Novel Data Prediction Data 20240227.xlsx
```

## 生成或刷新输入文件

```bash
python3 study4/prepare_inputs.py
```

生成内容包括：

- `study4_tasks.json` / `study4_tasks.csv`：6 个作者 prediction tasks
- `real_country_data.csv`：作者公开真实数据列
- `real_country_data_compact.csv`：只保留六个 Real 分析列的简表

`real_country_data.csv` 和 `real_country_data_compact.csv` 只保留真实国家数据列，不导出作者原始 GPT-3.5/GPT-4 预测结果。作者 GPT 预测结果属于原论文结果，不应作为第三方复现实验的输入。

## 作者 Study 4 设计

Study 4 包含 6 个任务：

- `implicit_sexuality_prediction`
- `explicit_sexuality_prediction`
- `implicit_age_prediction`
- `explicit_age_prediction`
- `implicit_gender_science_prediction`
- `explicit_gender_science_prediction`

每个任务重复 5 次。

因此，对每个模型，默认运行：

```text
6 tasks × 5 repeats = 30 conversations
```

## LLM API 配置

运行器使用 OpenAI-compatible 的 chat-completions API，默认从全局配置文件读取模型提供商：

```text
model_providers.yaml
```

正式运行前，先在该文件中填写 `base_url`、`api_key`、`model`、`max_concurrency` 和 `timeout`。如果文件中有多个提供商，可用 `--provider` 选择其中一个。

## Dry run 测试

```bash
python3 study4/run_study4.py --dry-run --limit 1 --repeats 1
```

## 正式运行 Study 4

```bash
python3 study4/run_study4.py --repeats 5 --sleep 1
```

默认流程是两轮对话：

1. 发送作者原始 initial prompt。
2. 记录模型回应。
3. 在同一对话中发送 follow-up prompt。
4. 保存模型国家级预测分数。

作者材料还说明，GPT-3.5 的 implicit predictions 曾额外使用一个类似材料末尾示例的 follow-up 来确认 D-score 方向。若复现者需要在 implicit 任务后执行这一方向确认，可加入：

```bash
python3 study4/run_study4.py --repeats 5 --confirm-implicit-direction --sleep 1
```

## 原始输出格式

模型原始响应保存为 JSONL：

```text
study4/outputs/raw_model_responses/study4_novel_data_predictor.jsonl
```

每一行包含：

- `timestamp_utc`
- `study`
- `provider`
- `model`
- `base_url`
- `timeout`
- `max_concurrency`
- `task`
- `title`
- `repeat`
- `initial_prompt`
- `followup_prompt`
- `initial_response`
- `final_response`
- `direction_check_prompt`
- `direction_check_response`
- `initial_raw`
- `final_raw`
- `direction_check_raw`

其中 `final_response` 是需要抽取国家预测分数的主要文本。

## 预测分数抽取

使用：

```text
study4/audit/prediction_extraction_template.csv
```

每个国家/地区的一次预测对应 CSV 中一行。

核心字段：

- `task`
- `repeat`
- `country`
- `predicted_score`
- `extraction_status`
- `coder`
- `notes`

模型每次 response 通常应包含作者 prompt 要求的 36 个国家/地区预测分数。抽取时如果出现国家缺失、名称变体、多个数值、范围外数值、只有排序没有分数，或 implicit D-score 方向解释不清，应在 `extraction_status` 和 `notes` 中记录。

Implicit tasks 使用 IAT D-score 范围 `-2.00` 到 `2.00`；explicit tasks 使用平均量表分数范围 `1.00` 到 `7.00`。启用 `--confirm-implicit-direction` 时，`direction_check_response` 只作为方向解释辅助，不替代 `final_response` 中的国家预测分数。

## 相关分析

当复现者填好 `predicted_score` 后，运行：

```bash
python3 study4/analyze_predictions.py
```

默认输出：

```text
study4/outputs/analysis/prediction_correlations.csv
```

脚本会按 `model × task × repeat` 计算模型预测分数与真实国家数据之间的 Pearson correlation。

作者 prompt 中使用 `South Korea`，真实数据表中对应国家名称为 `Korea`；分析脚本会自动映射。真实数据表中还包含 `(United States)`，但作者 prompt 未要求预测美国，因此相关分析默认不使用美国行。