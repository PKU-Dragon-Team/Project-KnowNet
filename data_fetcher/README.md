# A-数据获取模块（data_fetcher） tutorial
目前本模块有IEEE和Scopus两个爬虫，可以爬取元数据和论文原文。
能爬取到的字段有（暂缺的字段用None表示）：
|字段       |IEEE   |Scopus |
|---        |---    |----   |
|source     |√      |√      |
|title      |√      |√      |
|abstract   |部分内容*|√      |
|keywords   |X      |√      |
|type       |√      |√      |
|publication|√      |√      |
|year       |√      |√      |
|month      |X      |√      |
|volume     |√      |√      |
|issue      |√      |√      |
|authors.order                  |√      |√      |
|authors.isCorrespondingAuthor  |X      |√      |
|authors.normalizedName         |√      |√      |
|authors.firstName              |√      |√      |
|authors.lastName               |√      |√      |
|authors.orcid                  |X      |X      |
|authors.address                |X      |√      |
|authors.nationality            |X      |√      |
|authors.organization           |X      |√      |
|references中各字段              |X      |√      |
|文献全文                        |PDF格式|json格式|
\*摘要部分内容指摘要的大约前60个词，以省略号"..."结尾。

## 文献检索和元数据爬虫
### 1. IDManager类
系统要给每篇文献，包括爬取到元数据的文献和从元数据参考文献字段中解析出的引文，一个系统中唯一的ID。这个分配ID的任务将在数据获取阶段通过`IDManager`完成。

文献标题和ID的对应关系使用MongoDB存储在`paper_id`集合中。该集合文件格式如下所示：
```json
{
    {"id_": 1, "title": "Advanced Mathematics"}, 
    {"id_": 2, "title": "Linear Algebra"}, 
    {"id_": 3, "title": "Data Structure and Algorithm"},
    ... 
}
```
`IDManager`的使用方法如下：
```python
from data_fetcher.id_manager import IDManager   # 导入类
from data_platform.config import ConfigManager

config = ConfigManger({
    "init": {
        "uri": None,
        # MongoClient要连接的地址。如果在本机上运行写None即可。
        "database": "db",   
        # 如果数据是导入的，填写数据库名。
    },
})

id_manager = IDManager(
    config = config,
    key = ("paper_id", "title"),        
    # 表示我们要管理的文献名存储在paper_id集合中的title字段下
    auto_inc = ("id_inc", "paper_id")   
    # 文献ID是自增的，我们在id_inc集合中的paper_id字段记录当前ID增到哪个数字了。
)
```
后面的代码在使用爬虫时不需要写，但可以帮助您了解`IDManager`的工作原理。
```python
id_manager.get_id("Advanced Mathematics")
# 如果标题为Advanced Mathematics在paper_id中记录过，则返回对应的ID；如果没有出现过，则将其插入paper_id集合并返回新分配的ID。

id_manager.get_name(5)
# 返回编号为5的文献名。如果没有则返回None。

id_manager._get_db()
# 获取IDManager管理的pymongo.database.Database对象。debug时可以用到。
```

### 2. IEEE元数据爬虫
#### 实现原理

模拟用户向IEEE Xplore检索界面发送检索请求，获取返回的论文元数据，并存储在数据库的`metadata`字段中。

#### 使用教程

以下是示例代码：
```python
from data_fetcher.ieee.ieee_retrieval import IEEERetrieval  # 导入IEEE爬虫类
from data_platform.datasource.mongodb import MongoDBDS      # 导入mongodb数据源，存储元数据结果用
ieee_retrieval = IEEERetrieval(
    query = 'text mining',          # 检索关键词
    paper_id_manager = id_manager,  # 用于管理文献编号的IDManager
    offset = 0,                     # 开始爬取元数据偏移量
    num_result = 50,                # 爬取的数量。-1表示全部。
    request_interval = 5,           # 两次请求间隔时间（默认5秒）
    paper_set = 'a_topic'   # 表示这条元数据要放到哪个paper_set中。如果哪个都不放则留空。
)
# 上面定义的这个类即表示爬取以text mining为检索词检索得到的，从头开始的前50篇检索结果的元数据。
# 当要爬取大量数据时（如：10000篇元数据），建议以1000篇以内为一个单位少量多次地爬取并存储，这样发生异常时损失不会太大。

# 发起检索，获取IEEE服务器返回的元数据。
# 由于相邻两次请求中有间隔时间，因此本工作很耗时。建议在网络条件好的情况下使用。
# 最后将获取的元数据解析成系统格式并返回
ieee_metadata = ieee_retrieval.retrieve()

# 使用和前面IDManager相同的配置创建一个存储结果用的mongodb数据源
# 将ieee_retrieval检索得到的所有元数据存储到数据库中
mongodb = MongoDBDS(config)
ieee_retrieval.save(mongodb)
```

### 3. Scopus元数据爬虫
#### 实现原理
使用Elsevier提供的API获取元数据，并存储在数据库的`metadata`字段中。
由于Elsevier的API中检索和获取元数据是两个不同的接口，因此定义了`ScopusRetrieval`和`ScopusMetadataSpider`两个类。

#### 使用教程
**请在校园网环境等已订阅的条件下访问，不然可能无法获取作者、参考文献等字段！**
您需要在`https://dev.elsevier.com/`上获取一个API key。随后创建一个如下所示的`config.json`文件（推荐存储在`./data_fetcher/scopus/config.json`）：
```json
// config.json
{
    "apikey": "4719fe9f53c1bc699307a4f4c4ccf988",
    "insttoken": ""
}
```

以下是示例代码：
```python
from data_fetcher.scopus.scopus_retrieval import ScopusRetrieval
from data_fetcher.scopus.scopus_metadata_spider import ScopusMetadataSpider
# 导入Scopus爬虫类

sr = ScopusRetrieval(
    query = '2019-nCoV',            # 检索词
    # 爬取的数量。API规定不应超过5000。-1表示全部。
    num_result = 30                 
    # 含有apikey的json文件地址。默认为'./data_fetcher/scopus/config.json'
    config = './data_fetcher/scopus/config.json'
)

sr.retrieve()                   # 发起检索
doi_list = sr.get_doi_list()    # 获取检索结果的doi列表

for doi in doi_list:
    sms = ScopusMetadataSpider(
        doi = doi,              # 要获取元数据的论文的doi
        paper_id_manager = id_manager,
        config = './data_fetcher/scopus/config.json'
        paper_set = 'a_topic'   # 表示这条元数据要放到哪个paper_set中。如果哪个都不放则留空。
    )

    # 执行元数据获取操作，返回系统格式的元数据
    metadata = sms.execute()

    # 使用和前面IDManager相同的配置创建一个存储结果用的mongodb数据源
    # 将sms获取的元数据存储到数据库中
    mongodb = MongoDBDS(config)
    sms.save(mongodb)
```

## 文献全文爬虫
### 1. IEEE全文爬虫
#### 实现原理
通过IEEE全文数据库维护的articleNumber构造post请求，获取文献全文PDF的URL并下载PDF。articleNumber可以在IEEERetrieval结果中的`articleNumber`字段获取。

IEEE全文获取也是通过模拟用户访问请求，而不是调用API实现的。
#### 教程
**请在校园网环境等已订阅的条件下访问！**
以下是示例代码：
```python
from data_fetcher.ieee.ieee_fulltext_spider import IEEEFulltextSpider
ifs = IEEEFulltextSpider(
    article_number = '6221132',             # IEEE的ArticleNumber
    filename = 'my_lovely_paper.pdf',       # 保存PDF的文件名。默认article_number + '.pdf'
    output_path = './data/',                # 保存PDF的路径。默认'./data/'
    log_file = 'the_annoying_log.txt'       # 存放爬取失败的日志
)
res = ifs.execute()   # 执行爬虫，下载article_number对应的PDF全文。
# 返回值res为True表示获取成功，False表示获取失败，常见原因是该资源不存在。
```
之后就可以去`output_path`目录下查看结果了。

**众所周知，为应对目标服务器的反爬机制，我们应该在两次请求之间设定一定的时间间隔。**
`execute()`中设置了10s的间隔，加上PDF下载的时间，爬一篇PDF全文平均要15s。如果要爬取大量文献，请提前预估好时间（如：10000篇大约需要150000s，即42h）。

### 2. Scopus全文爬虫
#### 实现原理
使用Elsevier提供的API，根据doi获取json格式的全文数据。

#### 教程
**请在校园网环境等已订阅的条件下访问！**
以下是示例代码：
```python
from data_fetcher.scopus.scopus_fulltext_spider import ScopusFulltextSpider
sfs = ScopusFulltextSpider(
    doi = '10.1016/j.ijcard.2017.02.078',
    filename = 'my_lovely_paper.json',       # 保存PDF的文件名。默认doi（将'/'替换成'_'后） + '.json'
    output_path = './data/',                # 保存PDF的路径。默认'./data/'
    log_file = 'the_annoying_log.txt'       # 存放爬取失败的日志
)

res = sfs.execute()   # 执行爬虫，获取原文对应的XML数据
# 返回值res为True表示获取成功，False表示获取失败，常见原因是该资源不存在。
```
之后就可以去`output_path`目录下查看结果了。

### 全文爬虫注意事项
全文爬虫只负责根据doi、articleNumber等文献标识符下载文献，并不负责更新元数据中的`uri`字段。

如果你下载的全文在元数据中出现过，请自行使用MongoDBDS更新元数据中的`uri`字段。具体更新方式为（以Scopus全文爬虫为例）：
```python
from data_platform.datasource.mongodb import MongoDBDS
mongodb = MongoDBDS(config)     # 初始化MongoDBDS接口
sfs = ScopusFulltextSpider(doi='xxx')
file_addr = sfs.execute()
mongodb.query_and_update_doc('metadata', key={'doi': 'xxx'}, val={'uri': file_addr})  # 第一个参数为元数据所在的docset
```

## 后记
文档更新时间：2020-04-22

如有疑问请联系wangyueqian@pku.edu.cn
