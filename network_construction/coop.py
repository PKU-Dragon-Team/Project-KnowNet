# encoding:utf-8
from . import network as nw
from . import database as db
# 此模块用于提供对外接口
# 使用方法；1.使用create_db()方法建立一个图数据库，名称自定。2.使用几种XXX_network()方法构建网络。


# 此方法用于建立一个图数据库
# 参数database_name: 字符串类型，用于指定图数据库的名称，比如"first" / "new_database"等字符串书写格式
# 注意：需要修改图数据库建立的地址信息和图数据库的格式（也即file_format），请到database.py的init()函数中修改，由于这一改动不频繁，这里不提供接口。
def create_db(database_name):
    db.create_database(database_name)


# 此方法用于建立词语网络
# 参数node：字符串类型，取值为 "noun" / "adj" / "verb" / "noun_phrase" / "keyword" / "ner"
# 参数relation：字符串类型，取值为 "co" / "wordnet"，前者表示基于词语共现信息提取关系；后者基于wordnet，但是后者速度十分缓慢，建议数据量<10篇文档。
# 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
# 参数database：字符串类型，为您已经建立好的图数据库的名称
def text_network(node, relation, document, database):
    nw.create_network_text("ScienceDirectDataSource", document, node, relation, database)


# 此方法用于建立作者网络
# 这里建立的关系包括了引文关系，被引关系，属性名为cite co co_cite三种
# 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
# 参数database：字符串类型，为您已经建立好的图数据库的名称
def author_network(document, database):
    nw.create_network_author("ScienceDirectDataSource", document, "all", database)


# 此方法用于建立文章网络
# 这里建立的关系只包含文章的引用关系（属性名为cite）
# 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
# 参数database：字符串类型，为您已经建立好的图数据库的名称
def paper_network(document, database):
    nw.create_network_author("ScienceDirectDataSource", document, "cite", database)
