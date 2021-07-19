1. 运行 `main_clawer.py` 可以运行爬虫，爬取结果放在 `crawler/result/data.json`中，是以 url 的方式存在的（即未下载仓库文件）
2. `main_download_repos.py` 里面的[该段代码](https://github.com/yjqiang/github-crawler/blob/b0bebf69a243b4fd5ede21221d916ad240f3b93e/main_download_repos.py#L25-L48)可以实现下载某仓库的需求
3. `main_analyze.py` 可以分析 `download_repos` 路径下所有 zip 文件，并利用 `ast` 模块分析使用 `torch` 的 api，输出统计每种 api 的使用次数
4. `visualize.py` 可以对 `main_analyze.py` 的分析结果进行可视化