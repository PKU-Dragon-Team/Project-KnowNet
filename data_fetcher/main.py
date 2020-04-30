import os
from pathlib import Path

from data_fetcher.id_manager import IDManager
from data_fetcher.ieee.ieee_retrieval import IEEERetrieval
from data_fetcher.ieee.ieee_fulltext_spider import IEEEFulltextSpider
from data_fetcher.parser.pdf_parser import PDFParser, PDFFormat
from data_platform.config import ConfigManager
from data_platform.datasource.abc.doc import DocKeyPair
from data_platform.datasource.mongodb import MongoDBDS

current_path = Path(os.path.join(os.getcwd(), ".."))
data_path = current_path / 'data'
xml_path = data_path / 'unprocessed_articles_xml'
pdf_path = data_path / 'pdf_files'
config = ConfigManager({
    "init": {
        "location": xml_path,
        "pdf": pdf_path,
        'uri': None,
        'database': 'db'
    }
})


def main(query, paper_set, num_result):

    # 创建mongoDB数据源管理
    mgdbds = MongoDBDS(config=config)

    # 指定ID管理器
    pim = IDManager(
        config=config,
        key=DocKeyPair('paper_id', 'title'),
        auto_inc=DocKeyPair('id_inc', 'paper_id')
    )

    # 指定IEEE爬虫
    ir = IEEERetrieval(
        query=query,
        offset=0,
        num_result=num_result,
        paper_id_manager=pim,
        paper_set=paper_set
    )
    ir_res = ir.retrieve()     # 执行检索
    ir.save(mgdbds)         # 将检索结果记录在数据库中

    # IEEE全文爬虫+PDF解析
    article_numbers = [item['IEEEArticleNumber'] for item in ir_res]
    pdf_parser = PDFParser()
    for article_number in article_numbers:
        # 请注意：一定要在校园网环境下爬才能成功！
        ifs = IEEEFulltextSpider(
            article_number=article_number,
            request_interval=5
        )
        ifs_result = ifs.execute()  # 爬取PDF，记录爬取结果所在路径
        # 当然并不是所有原文都能成功爬到的，爬不到就会输出ERROR的log

        # 更新数据库中对应元数据的uri字段。
        # 可以整合到FullTextSpider类中，但这样会增加耦合，所以我还在思考
        if ifs_result:
            # 解析内容并保存
            content = pdf_parser.parse(ifs_result, pdf_format=PDFFormat.IEEE)
            mgdbds.query_and_update_doc(
                docset='metadata',
                query={'IEEEArticleNumber': article_number},
                val={'$set': {'uri': ifs_result, 'content': content}}
            )
            # 另外以后可以考虑改成多线程，这样爬IEEE的时候还能继续运行后面的程序

    # 此时./data中应该已经有几篇pdf了。
    # 检查现在数据库中的内容
    print(mgdbds.get_db().list_collection_names())
    print(list(mgdbds.get_db()['paper_id'].find()))
    print(list(mgdbds.get_db()['paper_set'].find()))
    print(list(mgdbds.get_db()['metadata'].find())[-1])  # 注意uri字段
    print(list(mgdbds.get_db()['id_inc'].find()))


def clear_database():
    mgdbds = MongoDBDS(config=config)
    # 将数据库原有内容清空
    mgdbds.clear()


if __name__ == '__main__':
    query_string = 'cancer'        # 检索词
    paper_set_string = 'cancer'    # 所属文献集
    paper_num = 3           # 爬取文献数
    # 主程序，使用前请保证安装了mongoDB，开启了mongoDB服务，并连接校园网等能下载外网全文数据的网络
    main(query_string, paper_set_string, paper_num)
