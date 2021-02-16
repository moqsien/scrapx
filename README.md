### 什么是 scrapx？

scrapx 是一个基于 scrapy 的定制包。其主要特点有：

- 优化了 scrapy 的 project 目录结构
  - 采用三层目录，分别是 workspace、project、spiders。其中 workspace 作为整个爬虫项目的目录，其下自动生成一个 scrapx_globals 目录用于存放整个爬虫项目都能自动加载的配置、中间件、pipeline 等。project 必须在 workspace 模块中。具体的爬虫则放在 project 下的 spiders 模块中。
- 去除了一些相对冗余的文件
  - 例如，在 project 中不再有 settings.py、pipeline.py、middleware.py 等文件。而是将 pipeline 和 middleware 统一放在 scrapx_globals，便于大项目的统一管理。原来的 settings.py 变为 run_xxx.py，同时自动生成的 run_xxx.py 更便于在 IDE 中以脚本形式运行，方便调试。
- 大量爬虫管理方案
  - 使用 MongoDB 作为存储 DB。在使用模板生成爬虫时，自动生成爬虫相关信息，修改之后，在爬虫第一次运行时，自动将爬虫信息存入 MongoDB，并自动生成一个唯一 id 用于标识该爬虫。每一次爬虫运行完毕，自动记录该次运行的统计数据到 MongoDB。一个 project，设计为同一类 data_type，用于归类不同类型的数据。
- 定制脚手架命令
  - 目前主要支持 initiate、genproject、genspider、crawl 四个命令，分别对应于创建 workspace、创建 project、创建 spider、命令行运行 spider。这些脚手架命令实现时使用 argparse 替换了已经废弃的 optparse。
- 完全兼容 scrapy 原有的配置参数
- 完全兼容 scrapy 原有的中间件、pipeline 接口
- 不影响原生 scrapy 的使用

### 如何使用 scrapx？

- clone 代码

```bash
git clone git@github.com:moqsien/scrapx.git
```

- 安装

```bash
# from source
cd scrapx
python setup.py build
python setup.py install
# from pypi
pip install scrapx
```

- 创建 workspace

```bash
scrapx -h # 查看命令
scrapx initiate example
```

- 创建 project

```bash
cd example
scrapx genproject test1
```

- 创建 spider

```bash
cd test1
scrapx genspider $spider_name $domain
```

- 接着就是根据用户自己的情况修改 scrapx_globals 的一些公共配置（如 MongoDB 参数等）、修改 run_xxx.py 中的 CRAWLER_INFO 等配置、编写爬虫，最后调试和运行。

- 命令行运行 spider

```bash
scrapx crawl tzrb # in a project
# or
scrapx crawl test1.tzrb # in a workspace
# or
# you can just run the run_xxx.py in an IDE
```

### scrapx 的目标

减少大型爬虫项目的冗余代码，方便管理和维护。

### TODO

- [ ] 类似 scrapyd 的部署工具开发
- [ ] 代理池集成
- [ ] 错误日志监控方案
- [ ] 部署和监控的可视化方案

### 声明

本项目仅做学习研究用，用户有因使用本项目造成的任何法律后果，与本项目无关。
