# Study 3：GPT 作为 Data Generator

本指南面向希望复现 Lehr et al. 2024 Study 3 方法流程的使用者。

Study 3 测试模型是否能根据训练语料中的文化知识，生成类似自然语言语料中观察到的性别刻板印象关联模式。

## 输入来源

prompt 来源于作者公开材料：

```text
materials_txt/Research Materials/GPT as Data Generator Materials 20240227.txt
```

词对 dyads 来源于作者公开 Excel 数据：

```text
【data and code】chatgpt-as-research-scientist-probing-gpt-s-capabilities-as-a-research-librarian-research-ethicist-data/Data and Codebooks/
```

对应文件：

- `GPT as Data Generator A - gender good-bad 20230227.xlsx`
- `GPT as Data Generator B - gender art-science 20230227.xlsx`
- `GPT as Data Generator C - gender home-work 20230227.xlsx`
- `GPT as Data Generator D - gender reading-math 20230227.xlsx`

## 生成或刷新输入文件

```bash
python3 study3/prepare_inputs.py
```

生成内容包括：

- `study3_prompts.json` / `study3_prompts.csv`：四个任务的作者 prompt
- `*_dyads.csv`：四个数据集各自的词对
- `all_dyads.csv`：合并后的全部词对
- `batch_plan.csv`：每一批次发送给模型的 prompt 和 dyads

`*_dyads.csv` 和 `all_dyads.csv` 只导出实验刺激字段，不包含作者原始 GPT-3.5/GPT-4 response。作者 response 是原论文结果，不应作为新模型复现实验的输入。

## 作者 Study 3 设计

Study 3 包含四类 gender stereotype 数据生成任务：

- `good_bad`：gender 与 good/bad 词的文化关联
- `art_science`：gender 与 art/science 词的文化关联
- `home_work`：gender 与 home/work 词的文化关联
- `reading_math`：gender 与 reading/math 词的文化关联

模型被要求对每个 dyad 给出 `1.0` 到 `10.0` 的评分，表示两个词在文化语料中共同出现或关联的强度。

## LLM API 配置

运行器使用 OpenAI-compatible 的 chat-completions API，默认从全局配置文件读取模型提供商：

```text
model_providers.yaml
```

正式运行前，先在该文件中填写 `base_url`、`api_key`、`model`、`max_concurrency` 和 `timeout`。如果文件中有多个提供商，可用 `--provider` 选择其中一个。

## Dry run 测试

```bash
python3 study3/run_study3.py --dry-run --limit 1
```

## 正式运行 Study 3

```bash
python3 study3/run_study3.py --sleep 1
```

默认流程是连续对话：

1. 发送 initial prompt。
2. 发送 first follow-up prompt。
3. 发送第一批 dyads 的 second follow-up prompt。
4. 按同一对话继续发送后续 dyad 批次。
5. 保存每轮模型原始响应。

## 原始输出格式

模型原始响应保存为 JSONL：

```text
study3/outputs/raw_model_responses/study3_data_generator.jsonl
```

其中 dyad 批次记录包含：

- `timestamp_utc`
- `study`
- `provider`
- `model`
- `base_url`
- `timeout`
- `max_concurrency`
- `dataset`
- `turn_type`
- `prompt_source`
- `batch_index`
- `batch_size`
- `first_random_id`
- `last_random_id`
- `dyads`
- `prompt`
- `response`
- `raw`

`response` 字段是需要抽取数值评分的模型原始文本。

## 响应抽取与分析

使用：

```text
study3/audit/score_extraction_template.csv
```

每个 dyad 对应 CSV 中一行。

核心字段：

- `extracted_score`：模型给出的 1.0-10.0 数值评分
- `extraction_status`：`ok`、`missing`、`ambiguous`、`out_of_range` 等
- `coder`：抽取/审核人
- `notes`：备注

后续基于抽取出的评分计算 WEAT D-score、single-category WEAT 和 alternative SC-WEAT 指标。

抽取时应逐 batch 定位每个 dyad 的评分。如果模型漏答、顺序错乱、给出多个数字、范围外数值或文本含糊，应在 `extraction_status` 和 `notes` 中记录。用于新模型复现的输入只应包含刺激字段，作者 Excel 中的 GPT-3.5/GPT-4 response 属于原论文结果，不应作为输入。

## 计算 WEAT / SC-WEAT 指标

当复现者把每个 dyad 的模型评分填入：

```text
study3/audit/score_extraction_template.csv
```

中的 `extracted_score` 字段后，可以运行：

```bash
python3 study3/analyze_scores.py
```

默认输出三张分析表：

```text
study3/outputs/analysis/weat_d_scores.csv
study3/outputs/analysis/single_category_weat_scores.csv
study3/outputs/analysis/alternative_sc_weat_scores.csv
```

`weat_d_scores.csv` 计算四个数据集的 Female vs Male、属性 A vs 属性 B 的 WEAT-style D-score。

`single_category_weat_scores.csv` 分别对 Female 和 Male 目标词计算单类别目标相对于两个属性类别的 SC-WEAT D-score。

`alternative_sc_weat_scores.csv` 分别对每个属性类别计算其相对于 Female 和 Male 目标词的 alternative SC-WEAT D-score。
