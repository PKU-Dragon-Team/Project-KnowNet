# 论文知识网络分析系统
Build status: [![Build Status](https://travis-ci.com/PKU-Dragon-Team/Project-KnowNet.svg?branch=master)](https://travis-ci.com/PKU-Dragon-Team/Project-KnowNet)

## 功能
A. 爬取开源的论文元数据及全文文本数据，并解析。

B. 基于论文元数据和文本，建构论文知识网络，包括作者、论文、词汇网络，关系类型包括合作、引用、共现等。

C. 分析论文知识网络的基本参数、重要节点、社团状况，并对网络进行可视化。

D. 存储并管理爬取的论文数据以及建构的论文知识网络，以供操作与分析。

E. 统一的UI界面，以供用户进行操作。

___

## 模块说明

### A-数据获取模块（data_fetcher）

爬虫程序，包括IEEE爬虫，其他爬虫待扩充。

    输入数据流：无。
    输出数据流：获取的论文元数据和文本数据存储于D模块的文档数据库，以供B模块取用。
> 具体内容见data_fetcher文件夹内说明。

### B-网络建构模块（network_construction）

利用论文元数据和文本数据建构网络,包括作者、论文、词汇网络，关系类型包括合作、引用、共现等，其他类型待扩充。

    输入数据流：从D模块的文档数据库获取A模块爬取的论文元数据和文本数据。
    输出数据流: 将建构的网络存储于D模块的图数据库，以供C模块取用。
> 具体内容见network_construction文件夹内说明。

### C-网络分析模块（network_analysis）

分析论文知识网络的基本参数、重要节点、社团状况，并对网络进行可视化。

     输入数据流：从D模块的图数据库获取B模块建构的论文知识网络。
     输出数据流：无。
> 具体内容见network_analysis文件夹内说明。

### D-数据基础平台（data_platform）

数据基础平台，存储并管理爬取的论文数据以及建构的论文知识网络，为A,B,C三个模块服务。

    1. document: **Working**
    2. datasource: _Partially Working_
    - json (DocDataSource): **Working** (except for _wildcard filtering_)
    - networkx (GraphDataSource): **Working** (except for _wildcard filtering_)
    - sqlite (RowDataSource): **Working** (except for _wildcard filtering_)
    - science_direct (DocDataSource): **Working** (except for _wildcard filtering_)
    3. utility: Not yet implemented
    4. config: **Working**
    5. log: Not yet implemented
> 具体内容见data_platform文件夹内说明。

### E-用户界面（views; UI.py）

系统UI，以供用户操作系统。

首先运行UI.py文件，之后在浏览器输入http://localhost:8080/construction，即可进入系统。

views文件夹内为各UI页面的template（基于bottle前端框架）。

### 其他文件与文件夹

1. `examples`：用例，针对爬虫（A模块）与数据基础平台（D模块），开发者可参考。
2. `test`：D模块的测试代码，开发者可参考。
3. `.gitignore`：这个文件的内容是一些规则，Git会根据这些规则来判断是否将文件添加到版本控制中。
4. `.pylintrc`：`pylint`的规范清单，在commit代码时检查代码是否符合给定规范。因为`pylint`默认的规范太严格，故用此文件放宽需求。
5. `.travis.yml`：Travis CI的配置文件，commit代码时被运行。
6. `LICENSE`：系统代码的开源协议。
7. `README.md`: 系统说明文件（本文件）。
8. `requirements.txt`：系统必备的外部包，安装时请用`pip install -r requirements.txt`安装全部包
9. `runtest.py`：代码commit时，按照该文件进行单元测试（判断是否符合`mypy`，`flake8`，`pylint`的代码规范），保证代码规范。不符合规范则无法commit。
10. `setup.cfg`：其他安装时的配置文件需求。