# 数据来源说明

本课使用 Federal Reserve 官网公开发布的 FOMC statement。每一篇 statement 是一条观测。

仓库不保存下载后的网页正文。读者运行 `01_download_text.py` 后，会在本地生成 HTML 缓存。

## 官方下载地址

| 日期 | 地址 | 教学标签 |
| --- | --- | --- |
| 2022-12-14 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20221214a.htm | hike |
| 2023-06-14 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20230614a.htm | hold |
| 2024-01-31 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20240131a.htm | hold |
| 2024-09-18 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm | cut |

## 标签含义

- `hike`：本次声明宣布提高联邦基金利率目标区间。
- `hold`：本次声明维持目标区间不变。
- `cut`：本次声明宣布降低目标区间。

这里的标签是教学用人工标签，用来演示“人工标签”和“规则识别”怎样互相核对。它不是完整的货币政策数据库。

## 使用边界

这些页面来自公开官方网站，但不同研究和课程对数据再分发有不同要求。稳妥做法是：

- 公开仓库只保存 URL 和代码。
- 读者自己运行代码下载文本。
- 论文或课程材料引用 Federal Reserve 官方页面。
- 不把本课 4 个样本的运行结果解释成真实经验事实。
