# 文本经济学方法课

![文本经济学方法课](assets/text_economics_methods_cover.png)

这是微信公众号栏目《文本经济学方法课》的公开学习仓库。它面向准备进入文本经济学的经济学、金融学、管理学和会计学研究者，从最基础的文本变量构造开始，逐步走到可复现的实证研究。

这个仓库的原则很简单：

- 告诉读者数据从哪里来，提供官方下载地址。
- 用一步一步的 Python 代码展示从下载、清洗、构造变量到检查输出的完整过程。
- 所有运行结果由读者在本地生成。

## 快速开始

建议使用 Python 3.10 或更新版本。

```bash
git clone https://github.com/Guch4ng/text-economics-methods.git
cd text-economics-methods
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS 或 Linux 用户可把激活环境命令替换为：

```bash
source .venv/bin/activate
```

Windows PowerShell 用户可以直接运行最新一课：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_lessons.ps1
```

运行指定课次：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_lessons.ps1 -Lesson 3
```

运行全部课程：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_lessons.ps1 -All
```

## 课程目录

| 课次 | 主题 | 位置 |
| --- | --- | --- |
| 第 1 课 | 文本如何成为经济变量：研究问题、观测单位、标签与效度 | [lessons/01_text_as_economic_variable](lessons/01_text_as_economic_variable) |
| 第 2 课 | 语料获取、编码、清洗、分句、分词与停用词 | [lessons/02_corpus_cleaning](lessons/02_corpus_cleaning) |
| 第 3 课 | 词频、关键词和词典法 | [lessons/03_word_frequency_dictionary](lessons/03_word_frequency_dictionary) |
| 第 4 课 | TF-IDF 与文本特征矩阵 | [lessons/04_tfidf_feature_matrix](lessons/04_tfidf_feature_matrix) |

## 第 1 课运行方式

```bash
python lessons/01_text_as_economic_variable/code/01_download_text.py
python lessons/01_text_as_economic_variable/code/02_clean_text.py
python lessons/01_text_as_economic_variable/code/03_build_variables.py
python lessons/01_text_as_economic_variable/code/04_check_outputs.py
```

运行后，本机会生成：

```text
.cache/lesson_01/
outputs/lesson_01/
```

这些目录不会上传到 GitHub。读者应自己运行代码生成结果。

## 第 2 课运行方式

```bash
python lessons/02_corpus_cleaning/code/01_download_html.py
python lessons/02_corpus_cleaning/code/02_clean_corpus.py
python lessons/02_corpus_cleaning/code/03_compare_terms.py
python lessons/02_corpus_cleaning/code/04_check_outputs.py
```

运行后，本机会生成：

```text
.cache/lesson_02/
outputs/lesson_02/
```

第 2 课重点检查：编码选择、正文抽取边界、分句样本、清洗前后高频词差异。

## 第 3 课运行方式

```bash
python lessons/03_word_frequency_dictionary/code/01_build_word_frequency_dictionary.py
```

运行后，本机会生成：

```text
outputs/lesson_03/
```

第 3 课重点检查：总词频、文档频率、关键词排序、文档-词矩阵和教学词典分数。

## 第 4 课运行方式

```bash
python lessons/04_tfidf_feature_matrix/code/01_build_tfidf_feature_matrix.py
```

运行后，本机会生成：

```text
outputs/lesson_04/
```

第 4 课重点检查：计数矩阵、IDF 表、TF-IDF 特征矩阵、区分性词和余弦相似度。

## 数据说明

第 1 至第 4 课使用 Federal Reserve 官网公开的 FOMC 声明。仓库只保存来源链接、教学标签和教学词典，不保存受限制数据。详见各课目录下的 `data_sources.md`。

## 学术使用提醒

本仓库示例用于教学，不直接构成经验研究结论。若用于论文，需要扩大样本、明确研究设计、进行人工复核、报告误差与稳健性检查。
