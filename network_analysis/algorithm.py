# coding=utf-8

from Network import *
# import numpy as np


def analysis_given_keyword_by_time(data, kw_list=None, field="keyword", centrality_type='degree',
                                   cumulative=False, topic_type="LSA"):
    """测试分年度分析关键词网络"""
    # data：数据源，来自wos_process.wos2paper的paperlist
    # kw_list：给定的关键词列表
    # field：关键词来源字段，keyword为来自作者关键词，title为来自标题，abstract为来自摘要
    # centrality_type：中心度类型
    # cumulative：布尔值，True使用按年累积的网络计算中心度，False按单个年份的网络计算中心度

    import wos_process
    import random
    import math
    from linear_regression import Linear_regression

    if field == "keyword":
        data = wos_process.divide_keyword(data)  # 将关键词短语切分成单词
    elif field == "title":
        data = wos_process.ti2de(data)  # 将标题切分成关键词
    elif field == "abstract":
        data = wos_process.ab2de(data)  # 将摘要切分成关键词
    plist = list()  # 年度文献数据列表
    times = range(1970, 2019)  # 预设时间跨度
    start_time = 1970  # 开始有文献的年份
    kw_dict = {topic[0]: dict() for topic in kw_list}  # 关键词，键为年份，值为{关键词：中心度}键值对
    for time in times:
        if cumulative:
            plist += wos_process.filter_paper_by_year(data, time)
        else:
            plist = wos_process.filter_paper_by_year(data, time)
        N = KeywordCooccurrenceNetwork(plist, from_external=True, from_file=False, include_review=False)
        if N.scale == 0:
            start_time += 1
            continue
        N = N.extract_max_component()  # 用最大主成分来计算，节约时间且对结果影响不大
        for topic in kw_list:
            kw_dict[topic[0]][time] = dict()  # 年度重要关键词词典，键为关键词，值为中心性大小
            for item in topic[1]:
                kw = item[0]
                if kw in N.network.nodes():
                    kw_dict[topic[0]][time][kw] = N.node_centrality(kw, centrality_type)
                else:
                    kw_dict[topic[0]][time][kw] = 0.0
        del N  # 释放内存
    del plist  # 释放内存
    if start_time < 2000:
        filename = "JASIST"
    else:
        filename = "JOI"
    for topic in kw_list:
        # 输出每个主题的趋势图
        plt.figure(figsize=(15, 10))
        plt.title("keywords of " + topic_type + " topic " + topic[0] + " in " + filename + " from " + field
                  + " measured by " + centrality_type + " centrality")  # 图表标题
        times = range(start_time, 2019)  # 实际时间范畴，x轴标度
        min_size = min([abs(item[1]) for item in topic[1]])  # 画图的最小宽度
        for item in topic[1]:
            kw = item[0]
            kw_value = list()
            for time in times:
                kw_value.append(kw_dict[topic[0]][time][kw])
            # kw_value = [kw_dict[topic[0]][time][kw] for time in times]
            # 用线性回归反映走势，标记代表走势
            # x_times = [time - min(times) for time in times]
            # data = [[a, b] for (a, b) in zip(x_times, kw_value)]
            # [b, m] = Linear_regression(data)  # 用线性回归拟合的直线
            # if m > 0.01:
            #     marker = 'o'
            # elif m < -0.01:
            #     marker = 'x'
            # else:
            #     marker = '.'
            if item[1] > 0:
                marker = 'o'
            else:
                marker = 'x'
            color = (random.uniform(0.0, 0.9), random.uniform(0.0, 0.9), random.uniform(0.0, 0.9))
            linewidth = 2 * item[1] / min_size
            if linewidth > 20:
                linewidth = 20 + math.log2(linewidth-19)        # 对倍数超出太多的进行对数化处理
            plt.plot(times, kw_value, color=color, label=kw, linewidth=linewidth, alpha=0.8, marker=marker)
        plt.legend(loc='upper right')
        plt.xlabel('year')
        plt.ylabel(centrality_type + ' centrality')
        plt.grid()
        plt.savefig(filename + '_' + field + '_' + centrality_type + '_' + topic_type + '_topic_' + topic[0] + '.png')
        # plt.show()
        plt.close()  # 释放内存
    del kw_dict  # 释放内存


def analysis_topic_by_time(data, topic_type="LSA", field="keyword", centrality_type='degree',
                           cumulative=False, num_topics=9, num_words=10):
    """测试分年度分析关键词网络"""
    # data：数据源，来自wos_process.wos2paper的paperlist
    # topic_type：主题类型，LSA或LDA
    # field：关键词来源字段，keyword为来自作者关键词，title为来自标题，abstract为来自摘要
    # centrality_type：中心度类型
    # cumulative：布尔值，True使用按年累积的网络计算中心度，False按单个年份的网络计算中心度

    import wos_process
    import random
    import math
    from linear_regression import Linear_regression

    if field == "keyword":
        data = wos_process.divide_keyword(data)  # 将关键词短语切分成单词
    elif field == "title":
        data = wos_process.ti2de(data)  # 将标题切分成关键词
    elif field == "abstract":
        data = wos_process.ab2de(data)  # 将摘要切分成关键词
    print("    " + field + "数据转换完成")
    if topic_type == "LSA":
        kw_list = get_lsa_keyword(data, field="keyword", all_topic=False, num_topics=num_topics, num_words=num_words)
    elif topic_type == "LDA":
        kw_list = get_lda_keyword(data, field="keyword", all_topic=False, num_topics=num_topics, num_words=num_words)
    plist = list()  # 年度文献数据列表
    times = range(1972, 2019)  # 预设时间跨度
    start_time = 1972  # 开始有文献的年份
    kw_dict = {topic[0]: dict() for topic in kw_list}  # 关键词，键为年份，值为{关键词：中心度}键值对
    for time in times:
        if cumulative:
            plist += wos_process.filter_paper_by_year(data, time)
        else:
            plist = wos_process.filter_paper_by_year(data, time)
        if len(plist) < 5:
            start_time += 1
            continue
        N = KeywordCooccurrenceNetwork(plist, from_external=True, from_file=False, include_review=False)
        if N.scale < 5:
            start_time += 1
            continue
        N = N.extract_max_component()  # 用最大主成分来计算，节约时间且对结果影响不大
        for topic in kw_list:
            kw_dict[topic[0]][time] = dict()  # 年度重要关键词词典，键为关键词，值为中心性大小
            for item in topic[1]:
                kw = item[0]
                if kw in N.network.nodes():
                    kw_dict[topic[0]][time][kw] = N.node_centrality(kw, centrality_type)
                else:
                    kw_dict[topic[0]][time][kw] = 0.0
        del N  # 释放内存
    del plist  # 释放内存
    if start_time < 2000:
        filename = "JASIST"
    else:
        filename = "JOI"
    for topic in kw_list:
        # 输出每个主题的趋势图
        plt.figure(figsize=(15, 10))
        plt.title("keywords of " + topic_type + " topic " + topic[0] + " in " + filename + " from " + field
                  + " measured by " + centrality_type + " centrality")  # 图表标题
        times = range(start_time, 2019)  # 实际时间范畴，x轴标度
        min_size = min([abs(item[1]) for item in topic[1]])  # 画图的最小宽度
        for item in topic[1]:
            kw = item[0]
            kw_value = list()
            for time in times:
                kw_value.append(kw_dict[topic[0]][time][kw])
            # kw_value = [kw_dict[topic[0]][time][kw] for time in times]
            # 用线性回归反映走势，标记代表走势
            # x_times = [time - min(times) for time in times]
            # data = [[a, b] for (a, b) in zip(x_times, kw_value)]
            # [b, m] = Linear_regression(data)  # 用线性回归拟合的直线
            # if m > 0.01:
            #     marker = 'o'
            # elif m < -0.01:
            #     marker = 'x'
            # else:
            #     marker = '.'
            if item[1] > 0:
                marker = 'o'
            else:
                marker = 'x'
            color = (random.uniform(0.0, 0.9), random.uniform(0.0, 0.9), random.uniform(0.0, 0.9))
            linewidth = 2 * item[1] / min_size
            if linewidth > 10:
                linewidth = 10 + math.log2(linewidth-10)    # 对倍数超过太多的进行对数处理
            plt.plot(times, kw_value, color=color, label=kw, linewidth=linewidth, alpha=0.8, marker=marker)
        plt.legend(loc='upper right')
        plt.xlabel('year')
        plt.ylabel(centrality_type + ' centrality')
        plt.grid()
        plt.savefig(filename + '_' + field + '_' + centrality_type + '_' + topic_type + '_topic_' + topic[0] + '.png')
        # plt.show()
        plt.close()  # 释放内存
    del kw_dict  # 释放内存


def analysis_top_keyword_by_time(data, field="keyword", centrality_type='degree', n=5, cumulative=False):
    """测试分年度分析关键词网络"""
    # data：数据源，来自wos_process.wos2paper的paperlist
    # field：关键词来源字段，keyword为来自作者关键词，title为来自标题，abstract为来自摘要
    # centrality_type：中心度类型
    # n：分析的热门关键词个数，注意n对应的是每个网络，最终会汇总所有关键词，结果的关键词数大于n
    # cumulative：布尔值，True使用按年累积的网络计算中心度，False按单个年份的网络计算中心度

    import wos_process
    import random
    from linear_regression import Linear_regression

    if field == "keyword":
        data = wos_process.divide_keyword(data)  # 将关键词短语切分成单词
    elif field == "title":
        data = wos_process.ti2de(data)  # 将标题切分成关键词
    elif field == "abstract":
        data = wos_process.ab2de(data)  # 将摘要切分成关键词
    plist = list()  # 年度文献数据列表
    times = range(1970, 2019)  # 预设时间跨度
    start_time = 1970  # 开始有文献的年份
    top_kw = dict()  # 重要关键词的词典，键为年份
    top_kw_set = set()  # 重要关键词的总集合
    net_dict = dict()  # 缓存每年的关键词网络数据，以供备用
    for time in times:
        if cumulative:
            plist += wos_process.filter_paper_by_year(data, time)
        else:
            plist = wos_process.filter_paper_by_year(data, time)
        N = KeywordCooccurrenceNetwork(plist, from_external=True, from_file=False, include_review=False)
        if N.scale == 0:
            start_time += 1
            continue
        net_dict[time] = N  # 缓存网络数据，以备用
        top_kw[time] = dict()  # 年度重要关键词词典，键为关键词，值为中心性大小
        for item in N.find_nodes_by_centrality(c_type=centrality_type, n=n):
            top_kw[time][item[0]] = item[1]
            top_kw_set.add(item[0])
    if start_time < 2000:
        filename = "JASIST"
    else:
        filename = "JOI"
    plt.figure(figsize=(15, 10))
    plt.title("top keywords in " + filename + " from " + field)  # 图表标题
    times = range(start_time, 2019)  # 实际时间范畴，x轴标度
    for kw in top_kw_set:
        kw_value = list()
        for time in times:
            if kw not in top_kw[time].keys():
                try:
                    top_kw[time][kw] = net_dict[time].node_centrality(c_type=centrality_type, node=kw)  # 在缓存网络中查中心度
                except:
                    top_kw[time][kw] = 0.0
            kw_value.append(top_kw[time][kw])
        if kw_value.count(0.0) < 3:  # 出现次数过少的被忽略
            # 用线性回归反映走势，标记代表走势
            # x_times = [time - min(times) for time in times]
            # data = [[a, b] for (a, b) in zip(x_times, kw_value)]
            # [b, m] = Linear_regression(data)  # 用线性回归拟合的直线
            # if m > 0.01:
            #     marker = 'o'
            # elif m < -0.01:
            #     marker = 'x'
            # else:
            #     marker = '.'
            color = (random.uniform(0.0, 0.9), random.uniform(0.0, 0.9), random.uniform(0.0, 0.9))
            marker = 'o'
            plt.plot(times, kw_value, color=color, label=kw, linewidth=2, alpha=0.8, marker=marker)
    plt.legend(loc='upper right')
    plt.xlabel('year')
    plt.ylabel(centrality_type + ' centrality')
    plt.grid()
    plt.savefig(filename + '_' + field + '_' + centrality_type + 'top keyword.png')
    # plt.show()


def get_lsa_topic(data, field="keyword", num_topics=9, num_words=5):
    """从给定的论文字段（field）通过LSA得出主题"""
    import wos_process
    from gensim import models, corpora
    data = wos_process.divide_keyword(data)
    if field == "keyword":
        data = wos_process.divide_keyword(data)
        data = wos_process.clean_keyword(data)
    elif field == "title":
        data = wos_process.ti2de(data)  # 将标题切分成关键词
    elif field == "abstract":
        data = wos_process.ab2de(data)  # 将摘要切分成关键词
    documents = [paper.de for paper in data]
    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]  # 生成语料库
    tf_idf = models.TfidfModel(corpus)  # 计算tf-idf

    # this may convert the docs into the TF-IDF space.
    # Here will convert all docs to TFIDF
    corpus_tfidf = tf_idf[corpus]

    # train the lsi model
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics)
    topics = lsi.show_topics(num_words=num_words, log=0)
    # for topic in topics:
    #     print(topic)
    # print()
    return topics


def get_lsa_keyword(data, field="keyword", all_topic=True, num_topics=9, num_words=5):
    # data: 输入的paperlist数据，由wos_process.wos2paper生成
    # field: 关键词来源字段，keyword代表作者关键词，title代表标题，abstract代表摘要
    # all_topic：布尔值，True返回所有topic的关键词（list，元素为str）
    #                   False返回单个topic的关键词（list，元素为tuple，tuple第一元为topic编号，第二元为关键词列表）
    # num_topics：LSA提取的主题数量
    # num_words：LSA主题内包含词汇的数量

    topics = get_lsa_topic(data, field, num_topics, num_words)
    kw = list()
    for topic in topics:
        tmp = topic[1].split(' + ')
        if all_topic:
            kw += [word[word.find("\"") + 1:word.rfind("\"")] for word in tmp]
        else:
            kw.append((str(topic[0] + 1), [(word[word.find("\"") + 1:word.rfind("\"")], eval(word[:word.find('*')]))
                                           for word in tmp]))
    if all_topic:
        kw = list(set(kw))
    return kw


def get_lda_topic(data, field="keyword", num_topics=9, num_words=5):
    """从给定的论文字段（field）通过LDA得出主题"""
    import wos_process
    from gensim import models, corpora
    data = wos_process.divide_keyword(data)
    if field == "keyword":
        data = wos_process.divide_keyword(data)
        data = wos_process.clean_keyword(data)
    elif field == "title":
        data = wos_process.ti2de(data)  # 将标题切分成关键词
    elif field == "abstract":
        data = wos_process.ab2de(data)  # 将摘要切分成关键词
    documents = [paper.de for paper in data]
    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]  # 生成语料库
    # train the lda model
    lda = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=num_topics)
    topics = lda.show_topics(num_words=num_words, log=0)
    # for topic in topics:
    #     print(topic)
    # print()
    return topics


def get_lda_keyword(data, field="keyword", all_topic=True, num_topics=9, num_words=5):
    # data: 输入的paperlist数据，由wos_process.wos2paper生成
    # field: 关键词来源字段，keyword代表作者关键词，title代表标题，abstract代表摘要
    # all_topic：布尔值，True返回所有topic的关键词（list，元素为str）
    #                   False返回单个topic的关键词（list，元素为tuple，tuple第一元为topic编号，第二元为关键词列表）
    # num_topics：LDA提取的主题数量
    # num_words：LDA主题内包含词汇的数量

    topics = get_lda_topic(data, field, num_topics, num_words)
    kw = list()
    for topic in topics:
        tmp = topic[1].split(' + ')
        if all_topic:
            kw += [word[word.find("\"") + 1:word.rfind("\"")] for word in tmp]
        else:
            kw.append(
                (str(topic[0] + 1),
                 [(word[word.find("\"") + 1:word.rfind("\"")], eval(word[:word.find('*')])) for word in tmp]))
    if all_topic:
        kw = list(set(kw))
    return kw


def _network2adjacency_matrix(N):
    """将网络转换成numpy邻接矩阵,返回值是numpy矩阵"""
    return nx.to_numpy_matrix(N.network, dtype=int)


'''
# 以下两个函数用于转化网络格式，暂时用不到，留作备用

def _adjacency_matrix2network(M, nodelist):
    """将numpy的无向邻接矩阵转换成networkx的Graph"""
    g = nx.Graph()
    g.add_nodes_from(nodelist)
    for i, row in enumerate(M):
        for j, element in enumerate(row.flat):
            if element:
                g.add_edge(nodelist[i], nodelist[j], weight=element)
    return g


def _adjacency_matrix2dinetwork(M, nodelist):
    """将numpy的有向邻接矩阵转换成networkx的DiGraph"""
    g = nx.DiGraph()
    g.add_nodes_from(nodelist)
    for i, row in enumerate(M):
        for j, element in enumerate(row.flat):
            if element:
                g.add_edge(nodelist[i], nodelist[j], weight=element)
    return g
'''


# 下面是一些支持的参数列表
# topic_types = ["LSA", "LDA"]
# fields = ["keyword", "title", "abstract"]
# centrality_types = ['degree', 'eigenvector', 'betweenness']
