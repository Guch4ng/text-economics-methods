# 第 2 课：语料获取、编码、清洗、分句、分词与停用词

本课目标：把公开网页变成可复核的干净语料，并检查清洗前后的词频差异。

这一课训练六个基础动作：

1. 从官方网页下载原始 HTML。
2. 检查声明编码、检测编码和最终选择编码。
3. 从网页中抽取 FOMC statement 正文。
4. 清理 HTML、空白符和特殊引号。
5. 把正文分成句子和词。
6. 比较整页文本、清洗正文、去停用词后的高频词。

## 观测单位

本课的观测单位仍是一篇 FOMC statement。每一篇声明会生成一条清洗诊断记录，并保存一份清洗后的正文。

## 数据从哪里来

本课数据来自 Federal Reserve 官网公开页面。仓库只保存 URL，不保存抓取后的网页正文。读者需要自己运行下载脚本。

详见 [data_sources.md](data_sources.md)。

## 运行步骤

请先在项目根目录安装依赖：

```bash
pip install -r requirements.txt
```

然后按顺序运行：

```bash
python lessons/02_corpus_cleaning/code/01_download_html.py
python lessons/02_corpus_cleaning/code/02_clean_corpus.py
python lessons/02_corpus_cleaning/code/03_compare_terms.py
python lessons/02_corpus_cleaning/code/04_check_outputs.py
```

## 每一步做什么

| 步骤 | 脚本 | 作用 |
| --- | --- | --- |
| 1 | `01_download_html.py` | 从 Federal Reserve 官网下载原始 HTML |
| 2 | `02_clean_corpus.py` | 选择编码、抽取正文、输出清洗语料和诊断表 |
| 3 | `03_compare_terms.py` | 比较整页文本、清洗正文、去停用词后的高频词 |
| 4 | `04_check_outputs.py` | 打印 Markdown 表格，帮助读者检查结果 |

## 本机会生成什么

运行后会出现两个目录：

```text
.cache/lesson_02/raw_html/
.cache/lesson_02/clean_text/
outputs/lesson_02/
```

`.cache/` 保存下载和清洗后的本地文件，`outputs/` 保存读者自己生成的结果。这两个目录被 `.gitignore` 排除，不应提交到 GitHub。

## 研究设计提醒

本课只用 4 篇声明演示语料处理流程。它能说明“网页文本为什么需要清洗”，但不能支持关于货币政策沟通的经验结论。真正写论文时，需要更大样本、稳定的数据管线、人工抽查、异常记录和可复现审计。
