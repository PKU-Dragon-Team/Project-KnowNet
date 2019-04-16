# A-数据获取模块（data_fetcher） tutorial

## IEEE爬虫（ieee_crawler）
**原理**

模拟向IEEE Xplore界面发送请求，根据检索结果元数据中的信息获取pdf的url，然后再访问url以下载pdf。

**载入工程**
```
from ieee_crawler import IEEECrawler
```

**创建IEEE爬虫类**
```
crawler = IEEECrawler(keyword)
```

参数：

keyword：关键词（相当于要输入检索框中的内容）

metadata_filename（选填）： 暂时保存检索结果元数据的文件名。默认为'metadata.txt'。

**模拟检索并获取元数据**
```
crawler.get_metadata()
```

参数：

pages_to_crawl（选填）：下载查询结果的前几个页面的元数据（每页有100篇文献）。默认为-1，即获取所有检索结果的元数据。

> 下载后的元数据会以文本格式保存在txt文件中。格式如下：
> [{"articleNumber":xxxxxxx},{"articleNumber":xxxxxxx},...]

**根据元数据下载pdf**
```
crawler.get_pdf()
```

参数：

pdf_start（选填）：从元数据中的第几条记录开始下载。默认为0。

pdf_end（选填）：到元数据中的第几条记录为止结束下载。默认为-1，即下载元数据中的所有项目的pdf文件。

> 下载后的pdf文件会保存在pdf_download文件夹中。
> 文件名为该文献在IEEE数据库中的唯一标识（articleNumber）。

**其他注意事项**

crawler_log.txt中会存储下载记录。如果出现
```
'cannot find pdf_url, doc_id = xxxx'
'Url visit error, pdf_url = xxxx'
'Cannot open file, filename = xxxx'
```

上述三种意外情况请后期手动处理。对于能正常下载的pdf，成功下载后会在下载记录文件中写入
```
'download successfully: xxxxxxx, no = id'
```
这里的id和第四步 “根据元数据下载pdf” 中pdf_start, pdf_end参数相对应。在受条件限制爬取过程发生间断时，可根据记录中的id调整pdf_start和pdf_end参数。
