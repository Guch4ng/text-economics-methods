# 第 4 课：TF-IDF 与文本特征矩阵

本课在词频矩阵基础上构造 TF-IDF 特征矩阵，找出每篇 FOMC 声明中更有区分度的词，并计算文档之间的余弦相似度。

## 运行方式

在仓库根目录运行：

```powershell
python lessons/04_tfidf_feature_matrix/code/01_build_tfidf_feature_matrix.py
```

运行后生成：

```text
outputs/lesson_04/clean_corpus_for_lesson04.csv
outputs/lesson_04/count_feature_matrix.csv
outputs/lesson_04/idf_table.csv
outputs/lesson_04/tfidf_raw_matrix.csv
outputs/lesson_04/tfidf_feature_matrix.csv
outputs/lesson_04/top_tfidf_terms_by_document.csv
outputs/lesson_04/distinctive_tfidf_terms_by_document.csv
outputs/lesson_04/cosine_similarity.csv
outputs/lesson_04/matrix_diagnostics.csv
outputs/lesson_04/tfidf_heatmap.png
```

## 数据

`data/source_urls.csv` 保存 4 篇 Federal Reserve FOMC 官方声明链接和教学标签。脚本运行时从官网抓取正文并构造特征矩阵。

## 输出解读

- `count_feature_matrix.csv`：原始计数矩阵。
- `idf_table.csv`：每个词的总次数、文档频率和 IDF。
- `tfidf_feature_matrix.csv`：L2 归一化后的 TF-IDF 矩阵。
- `distinctive_tfidf_terms_by_document.csv`：排除所有文档都出现的词后，每篇文档的高 TF-IDF 词。
- `cosine_similarity.csv`：基于归一化 TF-IDF 向量的余弦相似度矩阵。

本课样本只有 4 篇声明，所有结果只用于教学，不支持经验结论。
