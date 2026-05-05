# Lehr et al. 2024《ChatGPT as Research Scientist》方法流程复刻

本目录用于复刻以下论文的实验方法流程，并允许复现者配置不同的 LLM API 运行同样任务：

```text
Lehr et al. (2024). ChatGPT as Research Scientist:
Probing GPT's capabilities as a Research Librarian, Research Ethicist,
Data Generator, and Novel Data Predictor.
Proceedings of the National Academy of Sciences (PNAS).
DOI: 10.1073/pnas.2404328121
```

## API 配置

运行器使用 OpenAI-compatible 的 chat completions 接口。

默认从全局模型配置文件读取模型提供商信息：

```text
model_providers.yaml
```

配置格式示例：

```yaml
- name: kimi
  base_url: https://api.moonshot.cn/v1
  api_key: sk-...
  model: kimi-k2-turbo-preview
  max_concurrency: 50
  timeout: 60
```

如果文件中有多个提供商，可用 `--provider` 选择：

```bash
python3 reproduce.py study4 --provider kimi --repeats 5
```

若不传 `--provider`，默认使用配置文件中的第一个提供商。

正式运行前，把 `api_key` 替换成实际可用的 key。项目只保留这一种模型配置文件，不再维护单独的 `.env` 示例配置。

输出 JSONL 每条记录都会包含 `model` 字段，并同时记录 `provider`、`base_url`、`timeout` 和 `max_concurrency`，方便区分不同模型或 API 提供商的结果。

## 查看已解析材料

```bash
python3 reproduce.py materials
```

预期解析结果：

- Study 1：25 个 research-librarian 主题，分布在 5 个主题宽度等级中
- Study 2：18 个 initial prompts × 6 个 bad-research vignettes；另有 2 个 good-research vignettes
- Study 3：4 组 data-generator 词对数据
- Study 4：默认 6 个 prediction tasks × 5 次重复

## Study 1：Research Librarian

Study 1 已经被单独整理到：

```text
study1/
```

建议优先阅读：

```text
study1/README.md
```

运行：

```bash
python3 study1/run_study1.py --sleep 1
```

Study 1 遵循作者规则：要求模型找 20 篇有影响力的同行评审论文；如果模型第一次没有给够，则用 follow-up prompt 继续追问，其中 `x = 已给论文数`，`y = 20 - x`，直到给够 20 篇或模型明确承认无法完成。

更严格的方法一致性建议使用人工计数：

```bash
python3 study1/run_study1.py --manual-count
```

自动计数只是启发式估算，正式复现实验建议使用人工计数。作者最终的 correctness、completeness、relevance、hallucination 和 citation-count 编码需要人工或外部文献数据库核查。

## Study 2：Research Ethicist

Bad-research vignette study：

```bash
python3 study2/run_study2.py --sleep 1
```

Good-research supplementary vignette study：

```bash
python3 study2/run_study2.py --good --sleep 1
```

默认使用两轮对话结构：先发送 initial prompt，记录模型回应；再发送 vignette。这与作者材料中“initial prompt 先给出，然后复制 vignette”的流程一致。

正式方法复现不要使用 `--single-turn`；该选项仅用于流程检查。

rubric 已包含在作者材料中。本复现框架不自动打分，因为原论文使用人工 coder。

## Study 3：Data Generator

Study 3 已经被单独整理到：

```text
study3/
```

建议优先阅读：

```text
study3/README.md
```

```bash
python3 study3/run_study3.py --sleep 1
```

代码读取作者公开 Excel 中的 dyads，并按 `Random ID` 顺序呈现刺激材料。输入导出文件只保留实验刺激字段，不包含作者 GPT-3.5/GPT-4 response。材料文件给出了 initial prompt 和早期 follow-up 示例；后续批次按材料中描述的相同风格生成。

## Study 4：Novel Data Predictor

Study 4 已经被单独整理到：

```text
study4/
```

建议优先阅读：

```text
study4/README.md
```

```bash
python3 study4/run_study4.py --repeats 5 --sleep 1
```

这对应 SOM 中的设计：三个 constructs × implicit/explicit prediction × 每个任务 5 次重复。

输入导出的真实国家数据只保留 Real 数据列，不包含作者 GPT-3.5/GPT-4 预测结果。若需要复现材料中提到的 implicit D-score 方向确认 follow-up，可参考 Study 4 目录中的说明启用 `--confirm-implicit-direction`。
