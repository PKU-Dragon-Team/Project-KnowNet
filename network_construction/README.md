# B-网络构建模块(network_construction) tutorial

## 功能
1. 读取文档数据库，从数据库中获得各类论文元数据，以及元数据之间的各类关系。
2. 根据指定的数据源、数据量、节点类型和关系类型构建网络，并将网络存储在图数据库中。
3. 提供灵活的接口和独立的算法模块，用户可以轻松修改或增加网络类型、网络中的节点和关系类型。
4. 提供前端页面，用户可以从UI界面直接选择需要使用的数据源、数据量、节点和关系类型，以及指定存储的图数据库名称。

---

## 基础功能——作为仅调用用户的指南
1. 您直接使用的模块名称为coop.py
2. 您需要先导入模块（此条在后面不在赘述）
`from network_construction import coop`
3. 然后为了有效存储您建立的网络，您需要先创建一个数据库
`coop.create_db(database_name)`
参数database_name: 字符串类型，用于指定图数据库的名称，比如"first" / "new_database"等字符串书写格式。
返回值：若建立成功则返回0。
4. 接下来如果您需要修改图数据库所存储的地址信息和图数据库的格式（也即file_format），您可以到database.py的init()函数中修改存储地址和格式，由于这一改动不频繁，这里不提供接口。具体可改动内容见下方代码框。
修改一切数据存储的地址路径：更改data_location;
修改图数据库存储的路径：更改graph_location;
修改图数据库中文件存储的格式：修改file_format的取值，目前默认为graphml，一种XML格式，可读性强。
```
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        'file_format': 'graphml'
    })
```
5. 接下来您可以调用接口来构建您的网络。首先介绍如何构建词语网络，通过调用下面这个接口，就可以构建词语网络并存储在数据库中了。
`coop.text_network(node, relation, document, database)`
   + 参数node：字符串类型，取值为 "noun" / "adj" / "verb" / "noun_phrase" / "keyword" / "ner"
   + 参数relation：字符串类型，取值为 "co" / "wordnet"，前者表示基于词语共现信息提取关系；后者基于wordnet，但是后者速度十分缓慢，建议数据量<10篇文档。
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
   + 参数database：字符串类型，为您已经建立好的图数据库的名称
6. 调用下面的接口可以构建作者网络，具体说明如下：
`coop.author_network(document, database)`
   + 此方法用于建立作者网络
   + 这里图中建立的关系包括了引用关系，合著关系，属性名为cite co co_cite三种，分别表示引用，合著，引用+合著
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"两类形式，后者可以用下划线连接多组取值区间
   + 参数database：字符串类型，为您已经建立好的图数据库的名称
7. 调用下面的结构可以构建引文网络，具体说明如下：
`coop.paper_network(document, database)`
   + 此方法用于建立文章网络
   + 这里建立的关系只包含文章的引用关系（属性名为cite）
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
   + 参数database：字符串类型，为您已经建立好的图数据库的名称
8. 上述三个接口构建的网络均存储在对应的图数据库中，关于建立的网络更具体的节点的名称、属性名，您可以点开数据库直接查看（数据库为XML格式）。


## 进阶文档——如果您想构建更多的网络类型或有更多的参数选择
1. 您可以导入network.py模块和database.py模块。
2. 调用database模块中create_database(database_name)方法可以先建立一个数据库，database_name为数据库名称。
`database.create_database(database_name)`
3. 接下来通过封装好的网络构建模块network，您可以构建多种类型、多种关系的网络。
4. 下面的接口用于构建文本网络
`network.create_network_text(source, document, node, relation, database)`
   + 参数source：字符串类型，表示所使用数据的来源，可以指定建立网络所使用的文档数据库，目前可取值为ScienceDirectDataSource。
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
   + 参数node：字符串类型，取值为 "noun" / "adj" / "verb" / "noun_phrase" / "keyword" / "ner"
   + 参数relation：字符串类型，取值为 "co" / "wordnet"，前者表示基于词语共现信息提取关系；后者基于wordnet，但是后者速度十分缓慢，建议数据量<10篇文档。
   + 参数database：字符串类型，为您已经建立好的图数据库的名称
5. 下面的接口用来构建作者网络
`network.create_network_author(source, document, relation, database)`
   + 参数source：字符串类型，表示所使用数据的来源，可以指定建立网络所使用的文档数据库，目前可取值为ScienceDirectDataSource。
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
   + 参数relation：目前取值仅支持all，all 关系包括了 co-author 关系名 and cite 关系名 and co_cite关系名，也即这里图中建立的关系包括了引文关系，被引关系，属性名为cite co co_cite三种
   + 参数database：字符串类型，为您已经建立好的图数据库的名称
6. 下面的接口用来建立引文网络
`network.create_network_paper(source, document, relation, database)`
   + 参数source：字符串类型，表示所使用数据的来源，可以指定建立网络所使用的文档数据库，目前可取值为ScienceDirectDataSource。
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
   + 参数relation：目前仅支持 cite，也即引文关系，数据库中的属性名即为cite
   + 参数database：字符串类型，为您已经建立好的图数据库的名称
7. 下面的接口用于构建paper和author之间的创作网络，以及paper和word之间的文档词语网络
`network.create_other(source, document, relation, database)`
   + 参数source：字符串类型，表示所使用数据的来源，可以指定建立网络所使用的文档数据库，目前可取值为ScienceDirectDataSource。
   + 参数document：字符串类型，表示所取的文档的范围，取值示例 "1-10" / "1-10_20-30"
   + 参数relation：目前取值仅支持 paper_author和paper_word，数据库中存储的属性名称也是这两个字符串。两个网络的边均是paper指向author或word。
   + 参数database：字符串类型，为您已经建立好的图数据库的名称


## 进阶文档——如果您想创建更加丰富的、目前没有的节点类型，或者更加丰富的节点间关系
1. 解释：比如目前引文网络只支持cite关系，您想要添加其他关系；再比如您想为词语网络增加多几种类型的词语节点如代词。
2. 因为这些更丰富的抽取方法目前并没有算法实现，因此您需要先进入algorithm.py，增加对应的抽取算法，比如`extract_relation_keyword_co(text)`就是用来抽取关键词的共现关系。你构建新的抽取函数，实现算法即可。
3. 接下来，如果您需要丰富已有节点间的关系，只需要进入relation.py，模块内的接口名称等简单易懂。直接修改即可。
4. 接下来，如果您需要丰富节点的类型，则进入node.py即可，您只需要模仿已有的节点抽取方法，先抽取节点后，再存入数据库即可。代码书写的格式和方法完全参照已有实现即可。
5. 如果您想修改前端页面UI所提供的功能，或者界面展示形式，进入UI文件模仿已有实现简单修改即可，目前前后端协作可以正常运行，只需要修改您需要调用的函数名，和需要传输的参数名就可以了。