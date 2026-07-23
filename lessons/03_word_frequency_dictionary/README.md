# 第 3 课：词频、关键词和词典法

本课演示如何把清洗后的 FOMC 声明转换为词频表、关键词排序、文档-词矩阵和一个最小领域词典分数。

## 运行方式

在仓库根目录运行：

```powershell
python lessons/03_word_frequency_dictionary/code/01_build_word_frequency_dictionary.py
```

运行后生成：

```text
outputs/lesson_03/clean_corpus_for_lesson03.csv
outputs/lesson_03/top_terms.csv
outputs/lesson_03/document_term_matrix.csv
outputs/lesson_03/keywords_by_policy_label.csv
outputs/lesson_03/dictionary_scores.csv
outputs/lesson_03/dictionary_scores.png
```

## 数据

`data/source_urls.csv` 保存 4 篇 Federal Reserve FOMC 官方声明链接和教学标签。脚本运行时从官网抓取正文。

`data/domain_dictionary.csv` 是教学用最小领域词典，只用于说明词典变量如何构造，不是经过完整验证的货币政策沟通词典。

## 输出解读

- `top_terms.csv`：总词频、文档频率和每千词频率。
- `document_term_matrix.csv`：每行一篇声明，每列一个高频词。
- `keywords_by_policy_label.csv`：用带平滑的 log-odds 比较 `hike`、`hold`、`cut` 教学标签下更突出的词。
- `dictionary_scores.csv`：按 `inflation`、`labor`、`tightening`、`easing`、`uncertainty` 分类计算词典命中率。

本课样本只有 4 篇声明，所有结果只用于教学，不支持经验结论。
