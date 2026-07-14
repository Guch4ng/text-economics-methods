# 文本经济学方法课

![文本经济学方法课](assets/text_economics_methods_cover.png)

这是微信公众号栏目《文本经济学方法课》的公开学习仓库。它面向准备进入文本经济学的经济学、金融学、管理学和会计学研究者，从最基础的文本变量构造开始，逐步走到可复现的实证研究。

这个仓库的原则很简单：

- 不上传本地排版稿、公众号 HTML、中间输出和抓取后的正文。
- 告诉读者数据从哪里来，提供官方下载地址。
- 用一步一步的 Python 代码展示从下载、清洗、构造变量到检查输出的完整过程。
- 所有运行结果由读者在本地生成。

## 快速开始

建议使用 Python 3.10 或更新版本。

```bash
git clone https://github.com/YOUR-USER/text-economics-methods.git
cd text-economics-methods
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS 或 Linux 用户可把激活环境命令替换为：

```bash
source .venv/bin/activate
```

## 课程目录

| 课次 | 主题 | 位置 |
| --- | --- | --- |
| 第 1 课 | 文本如何成为经济变量：研究问题、观测单位、标签与效度 | [lessons/01_text_as_economic_variable](lessons/01_text_as_economic_variable) |

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

## 数据说明

第 1 课使用 Federal Reserve 官网公开的 FOMC 声明。仓库只保存来源链接和教学标签，不保存下载后的网页正文。详见 [data_sources.md](lessons/01_text_as_economic_variable/data_sources.md)。

## 学术使用提醒

本仓库示例用于教学，不直接构成经验研究结论。若用于论文，需要扩大样本、明确研究设计、进行人工复核、报告误差与稳健性检查。
