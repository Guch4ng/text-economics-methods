# 第 1 课：文本如何成为经济变量

本课目标：把一组公开政策声明整理成可以进入实证表格的文本变量。

这一课不追求复杂模型，只训练四个基础动作：

1. 明确数据来源和观测单位。
2. 从官方网页下载文本。
3. 清洗网页正文。
4. 构造词数、词典计数、标签和基础效度检查。

## 观测单位

本课的观测单位是一篇 FOMC statement。也就是说，最终表格中的每一行对应一篇声明，而不是一个句子、一个段落或一个词。

## 数据从哪里来

本课数据来自 Federal Reserve 官网公开页面。仓库只保存 URL，不保存抓取后的正文。读者需要自己运行下载脚本。

详见 [data_sources.md](data_sources.md)。

## 运行步骤

请先在项目根目录安装依赖：

```bash
pip install -r requirements.txt
```

然后按顺序运行：

```bash
python lessons/01_text_as_economic_variable/code/01_download_text.py
python lessons/01_text_as_economic_variable/code/02_clean_text.py
python lessons/01_text_as_economic_variable/code/03_build_variables.py
python lessons/01_text_as_economic_variable/code/04_check_outputs.py
```

## 每一步做什么

| 步骤 | 脚本 | 作用 |
| --- | --- | --- |
| 1 | `01_download_text.py` | 从 Federal Reserve 官网下载原始 HTML |
| 2 | `02_clean_text.py` | 从 HTML 中抽取声明正文并保存为 TXT |
| 3 | `03_build_variables.py` | 分词、统计词典、构造标签和变量表 |
| 4 | `04_check_outputs.py` | 检查输出表、打印 Markdown 表格、生成折线图 |

## 本机会生成什么

运行后会出现两个目录：

```text
.cache/lesson_01/raw_html/
.cache/lesson_01/clean_text/
outputs/lesson_01/
```

`.cache/` 保存下载和清洗后的本地文件，`outputs/` 保存读者自己生成的结果。这两个目录被 `.gitignore` 排除，不应提交到 GitHub。

## 研究设计提醒

本课只用 4 篇声明演示流程。它能说明“文本如何成为变量”，但不能支持关于货币政策效果的经验结论。真正写论文时，需要更大样本、清晰识别设计、人工复核和误差分析。
