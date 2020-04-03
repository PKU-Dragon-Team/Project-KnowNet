# A-数据获取模块（data_fetcher） tutorial
目前本模块有IEEE和Scopus两个文献元数据爬虫。
能爬取到的字段有：
|字段       |IEEE   |Scopus |
|---        |---    |----   |
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
\*摘要部分内容指摘要的大约前60个词，以省略号"..."结尾。

## 1. IDManager类
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

## 2. IEEE爬虫
### 实现原理

模拟用户向IEEE Xplore检索界面发送检索请求，获取返回的论文元数据。

### 使用教程

以下是示例代码：
```python
from data_fetcher.ieee.ieee_retrieval import IEEERetrieval  # 导入IEEE爬虫类
ieee_retrieval = IEEERetrieval(
    query = 'text mining',          # 检索关键词
    paper_id_manager = id_manager,  # 用于管理文献编号的IDManager
    offset = 0,                     # 开始爬取元数据偏移量
    num_result = 50,                # 爬取的数量。-1表示全部。
    request_interval = 5,           # 两次请求间隔时间（默认5秒）
)
# 上面定义的这个类即表示爬取以text mining为检索词检索得到的，从头开始的前50篇检索结果的元数据。
# 当要爬取大量数据时（如：10000篇元数据），建议以1000篇以内为一个单位少量多次地爬取并存储，这样发生异常时损失不会太大。

    
ieee_retrieval.retrieve()   
# 发起检索，获取IEEE服务器返回的元数据。
# 由于相邻两次请求中有间隔时间，因此本工作很耗时。建议在网络条件好的情况下使用。

ieee_metadata = ieee_retrieval.parse()     
# 将retrieve()获取的元数据解析成系统格式并返回
```

## 3. Scopus爬虫
### 实现原理
使用Elsevier提供的API获取元数据。
由于Elsevier的API中检索和获取元数据是两个不同的接口，因此定义了`ScopusRetrieval`和`ScopusMetadataSpider`两个类。

### 教程
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
    output_filename = 'xxx.json',   # 暂存检索结果的地址。一般用不到
    num_result = 30                 
    # 爬取的数量。API规定不应超过5000。-1表示全部。
    config = './data_fetcher/scopus/config.json'
    # 含有apikey的json文件地址。默认为'./data_fetcher/scopus/config.json'
    )

sr.retrieve()                   # 发起检索
doi_list = sr.get_doi_list()    # 获取检索结果的doi列表

for doi in doi_list:
    sms = ScopusMetadataSpider(
        doi = doi,              # 要获取元数据的论文的doi
        paper_id_manager = id_manager,
        config = './data_fetcher/scopus/config.json'
        )

    metadata = sms.execute()
    # 执行元数据获取操作，返回系统格式的元数据
```

## 4. 后记
文档更新时间：2020-04-02

如有疑问请联系wangyueqian@pku.edu.cn
