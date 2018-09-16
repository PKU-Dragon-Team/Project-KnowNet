# coding=utf-8

import networkx as nx
import community
import matplotlib.pyplot as plt
# 以下为系统中使用
from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS
from pathlib import Path
import os


def init():
    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        }
    })
    return NetworkXDS(config)


'''
# 以下两个函数是用wos测试用的，系统中不使用，此处只作备份

def _data2citationnetwork(data, include_review=True):
    """根据来自模块B的网络建构本模块需要的网络模块"""
    import wos_process  # 调试用
    # 需要根据data的数据结构补充
    plist = wos_process.wos2paper(data, include_review)
    g = wos_process.paper_net(plist, pt="J")
    return g


def _data2keywordnetwork(data, from_file=True, include_review=True):
    """根据来自模块B的网络建构本模块需要的网络模块"""
    import wos_process  # 调试用
    # 需要根据data的数据结构补充
    if from_file:
        plist = wos_process.wos2paper(data, include_review)
    else:
        plist = data
    g = wos_process.paper_net(plist, node="keyword", pt="J")
    return g
'''


class _DiNetwork:
    # 以下是初始化就会计算好的属性
    nxds = None             # 读取网络用模块
    network = nx.DiGraph()  # 存储网络数据，格式为networkx
    scale = 0  # 网络的规模，即节点数
    size = 0  # 网络的大小，即边数
    aver_degree = 0  # 网络的度均值（忽略入度和出度的区别）
    density = 0  # 网络的密度
    attribute = dict()  # 网络的固有属性，来自 B 数据处理模块
    _edge_weight = None  # 确定网络有无边权

    # 以下是初次调用才会计算的属性，以减少不必要的计算，调用时请使用对应的方法
    _connectivity = dict()  # 网络的连通度
    _centrality = dict()  # 网络的节点中心度
    _centralization = dict()  # 网络的中心势

    def __init__(self):
        # 中心度初始化，否则重复建类时会继承上一个实例的值
        self.nxds = init()
        self._connectivity = {"node": None,
                              "edge": None}  # 网络的连通度
        self._centrality = {"degree": None,
                            "indegree": None,
                            "outdegree": None,
                            "eigenvector": None,
                            "katz": None,
                            "pagerank": None,
                            "betweenness": None,
                            "closeness": None}  # 网络的节点中心度
        self._centralization = {"degree": None,
                                "indegree": None,
                                "outdegree": None,
                                "eigenvector": None,
                                "katz": None,
                                "pagerank": None,
                                "betweenness": None,
                                "closeness": None}  # 网络的中心势

    def nodes(self, data=False):
        """返回节点列表"""
        return self.network.nodes(data=data)

    def edges(self, data=False):
        """返回边列表"""
        return self.network.edges(data=data)

    def centrality(self, type='degree'):
        """计算整个网络的所有节点的中心度，返回一个dict"""
        if type not in self._centrality.keys():  # 检测输入类型不正确的异常
            raise ValueError(
                "输入类型不正确！type请输入degree/indegree/outdegree/eigenvector/katz/pagerank/betweenness/closeness！")
        if not self._centrality[type]:
            if type == 'degree':  # 因为networkx的度数中心度计算不带权重，故自制了一个
                if self._edge_weight:
                    weight = [edge[2]['weight'] for edge in self.network.edges(data=True)]
                    s = 1.0 / sum(weight)
                else:
                    s = 1.0 / (len(self.network) - 1.0)
                self._centrality[type] = {n: d * s for n, d in self.network.degree(weight=self._edge_weight)}
            elif type == 'indegree':
                s = 1.0 / (len(self.network) - 1.0)
                self._centrality[type] = {n: d * s for n, d in self.network.in_degree(weight=self._edge_weight)}
            elif type == 'outdegree':
                s = 1.0 / (len(self.network) - 1.0)
                self._centrality[type] = {n: d * s for n, d in self.network.out_degree(weight=self._edge_weight)}
            elif type == 'eigenvector':
                self._centrality[type] = nx.eigenvector_centrality(self.network, max_iter=1000,
                                                                   weight=self._edge_weight)
            elif type == 'katz':
                self._centrality[type] = nx.katz_centrality(self.network, max_iter=1000, weight=self._edge_weight)
            elif type == 'pagerank':
                pr = nx.pagerank(self.network, weight=self._edge_weight)
                self._centrality[type] = {node: pr[node] for node in pr}
            elif type == 'betweenness':
                self._centrality[type] = nx.betweenness_centrality(self.network, weight=self._edge_weight)
            elif type == 'closeness':
                self._centrality[type] = nx.closeness_centrality(self.network)
        return self._centrality[type]

    def node_centrality(self, node, type='degree'):
        return self.centrality(type=type)[node]

    def centralization(self, type='degree'):
        if type == 'degree':
            if not self._centralization['degree']:
                1  # 占位符
                # self.centralization['degree'] = nx.degree_centrality(self.network)        # 中心势计算之后补充
            return self._centralization
        elif type == 'betweenness':
            if not self._centralization['betweenness']:
                1  # 占位符
                # self.centralization['betweenness'] = nx.betweenness_centrality(self.network)
            return self._centralization
        elif type == 'closeness':
            if not self._centralization['closeness']:
                1  # 占位符
                # self.centralization['closeness'] = nx.closeness_centrality(self.network)
            return self._centralization
        else:
            raise ValueError("输入类型不正确！type请输入degree或betweenness或closeness！")

    def find_nodes_by_centrality(self, type='degree', n=1, return_value=True):
        """根据中心性抽取重要节点，n为抽取的节点个数
        return_value决定返回值为节点列表还是(节点，中心度)元组列表"""
        if n > self.scale:
            raise ValueError("n不能比网络节点数目还大！")
        nodelist = list()  # 缓存节点列表
        centrality = self.centrality(type=type)  # 缓存中心度词典
        for node in centrality:  # 遍历
            nodelist.append((node, centrality[node]))
        nodelist.sort(key=lambda x: x[1], reverse=True)  # 排序
        if not return_value:  # 去除中心度值
            nodelist = [item[0] for item in nodelist]
        return nodelist[:n]  # 返回前n个结果

    def draw_network(self, layout="spring"):
        """将网络可视化输出"""
        import math
        if self.scale > 300:  # 对于太大的网络，可视化意义不大且效率极低，故只对小型网络进行可视化
            print("网络规模太大，不支持可视化！请抽取更小的子网络进行可视化")
            return
        g = self.network
        node_labels = dict()  # 节点标签
        if layout == 'spring':  # 分散布局
            pos = nx.spring_layout(g, k=2 / math.sqrt(g.number_of_nodes()), iterations=100)
        elif layout == 'shell':  # 环形布局，中间是中心点
            center = [item[0] for item in self.find_nodes_by_centrality(type='degree', n=1)]
            pos = nx.shell_layout(self.network, nlist=[center, [item for item in g.nodes if item not in center]])
            node_labels[center[0]] = center[0].ti
        elif layout == 'spectral':  # 谱状布局，中间是中心点
            pos = nx.spectral_layout(self.network)
        else:
            raise ValueError("没有这种布局！")
        '''以下只是针对测试数据的一种可视化形式！
        实际还需根据B模块的数据格式调整'''
        node_colors = [(item.py - 1969) / 31 for item in g.nodes]
        node_sizes = [math.log2(item[1] + 1) * 20 + 1 for item in g.degree()]
        nx.draw_networkx_edges(g, pos, edge_color='#000000', width=1, with_labels=False, alpha=0.5)
        nx.draw_networkx_nodes(g, pos, node_color=node_colors, with_labels=False, node_size=node_sizes,
                               cmap=plt.cm.Reds, alpha=1, linewidths=0.5, edgecolors='k')
        nx.draw_networkx_labels(g, pos, labels=node_labels, font_size=10, font_color='#FFFFFF')
        # nx.draw(g, pos, nodelist = klist, node_color='b', edge_color=colors,
        #        width=4, edge_cmap=plt.cm.Reds, with_labels=False, node_size = 100, alpha = 0.5)
        plt.show()

    def draw_degree_distribution(self, percentage=False):
        """展示网络的度分布"""
        import math
        import linear_regression
        plt.figure(figsize=(8, 4))
        degree_list = [item[1] for item in self.network.degree]  # network.degree返回节点度数列表,每个元素为(节点,度数)二元组
        degree_set = set(degree_list)  # 后续对相同度数的节点计数用
        if percentage:  # 显示被引量为x的文章数的百分数
            degree_time_list = [(degree, degree_list.count(degree) / self.scale) for degree in degree_set]
        else:
            degree_time_list = [(degree, degree_list.count(degree)) for degree in degree_set]
        degree_time_list.sort(key=lambda i: i[0])  # 排序好的被引量list，第一个元素为被引量，第二个元素为对应被引量的文章数
        x = [math.log2(item[0] + 0.1) for item in degree_time_list]  # 将参数取双对数
        y = [math.log2(item[1]) for item in degree_time_list]
        data = [[a, b] for (a, b) in zip(x, y) if 3 <= a <= 6]
        [b, m] = linear_regression.Linear_regression(data)  # 用线性回归拟合的直线
        x_ = [3, 6]
        y_ = [3 * m + b, 6 * m + b]
        plt.plot(x_, y_, "c", linewidth=4, alpha=0.85, label="α=" + str(-m))
        plt.scatter(x, y, c="m", label="total citation")
        plt.xlabel("degree(log)")
        if percentage:
            plt.ylabel("percentage")
            plt.title("degree distribution in percentage")
        else:
            plt.ylabel("number(log)")
            plt.title("degree distribution(log)")
        plt.legend()
        plt.show()  # 显示图

    def draw_indegree_distribution(self, percentage=False):
        """展示网络的入度分布"""
        import math
        import linear_regression
        plt.figure(figsize=(8, 4))
        degree_list = [item[1] for item in self.network.in_degree]  # network.degree返回节点度数列表,每个元素为(节点,度数)二元组
        degree_set = set(degree_list)  # 后续对相同度数的节点计数用
        if percentage:  # 显示被引量为x的文章数的百分数
            degree_time_list = [(degree, degree_list.count(degree) / self.scale) for degree in degree_set]
        else:
            degree_time_list = [(degree, degree_list.count(degree)) for degree in degree_set]
        degree_time_list.sort(key=lambda i: i[0])  # 排序好的被引量list，第一个元素为被引量，第二个元素为对应被引量的文章数
        x = [math.log2(item[0] + 0.1) for item in degree_time_list]  # 将参数取双对数
        y = [math.log2(item[1]) for item in degree_time_list]
        data = [[a, b] for (a, b) in zip(x, y) if 3 <= a <= 6]
        [b, m] = linear_regression.Linear_regression(data)  # 用线性回归拟合的直线
        x_ = [3, 6]
        y_ = [3 * m + b, 6 * m + b]
        plt.plot(x_, y_, "c", linewidth=4, alpha=0.85, label="α=" + str(-m))
        plt.scatter(x, y, c="m", label="total citation")
        plt.xlabel("indegree(log)")
        if percentage:
            plt.ylabel("percentage")
            plt.title("indegree distribution in percentage")
        else:
            plt.ylabel("number(log)")
            plt.title("indegree distribution(log)")
        plt.legend()
        plt.show()  # 显示图

    def draw_outdegree_distribution(self, percentage=False):
        """展示网络的入度分布"""
        import math
        import linear_regression
        plt.figure(figsize=(8, 4))
        degree_list = [item[1] for item in self.network.out_degree]  # network.degree返回节点度数列表,每个元素为(节点,度数)二元组
        degree_set = set(degree_list)  # 后续对相同度数的节点计数用
        if percentage:  # 显示被引量为x的文章数的百分数
            degree_time_list = [(degree, degree_list.count(degree) / self.scale) for degree in degree_set]
        else:
            degree_time_list = [(degree, degree_list.count(degree)) for degree in degree_set]
        degree_time_list.sort(key=lambda i: i[0])  # 排序好的被引量list，第一个元素为被引量，第二个元素为对应被引量的文章数
        x = [math.log2(item[0] + 0.1) for item in degree_time_list]  # 将参数取双对数
        y = [math.log2(item[1]) for item in degree_time_list]
        data = [[a, b] for (a, b) in zip(x, y) if 3 <= a <= 6]
        [b, m] = linear_regression.Linear_regression(data)  # 用线性回归拟合的直线
        x_ = [3, 6]
        y_ = [3 * m + b, 6 * m + b]
        plt.plot(x_, y_, "c", linewidth=4, alpha=0.85, label="α=" + str(-m))
        plt.scatter(x, y, c="m", label="total citation")
        plt.xlabel("outdegree(log)")
        if percentage:
            plt.ylabel("percentage")
            plt.title("outdegree distribution in percentage")
        else:
            plt.ylabel("number(log)")
            plt.title("outdegree distribution(log)")
        plt.legend()
        plt.show()  # 显示图


class _Network:
    # 以下是初始化就会计算好的属性
    nxds = None  # 读取网络用模块
    network = nx.Graph()  # 存储网络数据，格式为networkx
    scale = 0  # 网络的规模，即节点数
    size = 0  # 网络的大小，即边数
    aver_degree = 0  # 网络的度均值
    density = 0  # 网络的密度
    attribute = dict()  # 网络的固有属性，来自 B 数据处理模块
    _edge_weight = None  # 确定网络有无边权

    # 以下是初次调用才会计算的属性，以减少不必要的计算，调用时请使用对应的方法
    _connectivity = dict()  # 网络的连通度
    _centrality = dict()  # 网络的节点中心度
    _centralization = dict()  # 网络的中心势

    def __init__(self):
        self.nxds = init()
        # 中心度初始化，否则重复建类时会继承上一个实例的值
        self._connectivity = {"node": None,
                              "edge": None}  # 网络的连通度
        self._centrality = {"degree": None,
                            "eigenvector": None,
                            "katz": None,
                            "pagerank": None,
                            "betweenness": None,
                            "closeness": None}  # 网络的节点中心度
        self._centralization = {"degree": None,
                                "eigenvector": None,
                                "katz": None,
                                "pagerank": None,
                                "betweenness": None,
                                "closeness": None}  # 网络的中心势

    def nodes(self, data=False):
        """返回节点列表"""
        return self.network.nodes(data=data)

    def edges(self, data=False):
        """返回边列表"""
        return self.network.edges(data=data)

    def centrality(self, type='degree'):
        """计算整个网络的所有节点的中心度，返回一个dict"""
        if type not in self._centrality.keys():
            raise ValueError("输入类型不正确！type请输入degree/eigenvector/katz/pagerank/betweenness/closeness！")
        if not self._centrality[type]:
            if type == 'degree':  # 因为networkx的度数中心度计算不带权重，故自制了一个
                if self._edge_weight:
                    weight = [edge[2]['weight'] for edge in self.network.edges(data=True)]
                    s = 1.0 / sum(weight)
                else:
                    s = 1.0 / (len(self.network) - 1.0)
                self._centrality[type] = {n: d * s for n, d in self.network.degree(weight=self._edge_weight)}
            elif type == 'eigenvector':
                self._centrality[type] = nx.eigenvector_centrality(self.network, max_iter=1000,
                                                                   weight=self._edge_weight)
            elif type == 'katz':
                self._centrality[type] = nx.katz_centrality(self.network, max_iter=10000, tol=1e-03,
                                                            weight=self._edge_weight)
            elif type == 'pagerank':
                pr = nx.pagerank(self.network, weight=self._edge_weight)
                self._centrality[type] = {node: pr[node] for node in pr}
            elif type == 'betweenness':
                self._centrality[type] = nx.betweenness_centrality(self.network, weight=self._edge_weight)
            elif type == 'closeness':
                self._centrality[type] = nx.closeness_centrality(self.network)
        return self._centrality[type]

    def node_centrality(self, node, type='degree'):
        return self.centrality(type=type)[node]

    def centralization(self, type='degree'):
        if type == 'degree':
            if not self._centralization['degree']:
                1  # 占位符
                # self.centralization['degree'] = nx.degree_centrality(self.network)        # 中心势计算之后补充
            return self._centralization
        elif type == 'betweenness':
            if not self._centralization['betweenness']:
                1  # 占位符
                # self.centralization['betweenness'] = nx.betweenness_centrality(self.network)
            return self._centralization
        elif type == 'closeness':
            if not self._centralization['closeness']:
                1  # 占位符
                # self.centralization['closeness'] = nx.closeness_centrality(self.network)
            return self._centralization
        else:
            raise ValueError("输入类型不正确！type请输入degree或betweenness或closeness！")

    def find_nodes_by_centrality(self, type='degree', n=1, return_value=True):
        """根据中心性抽取重要节点，n为抽取的节点个数，
        return_value决定返回值是节点列表还是(节点，中心度)元组列表"""
        if n > self.scale:
            raise ValueError("n不能比网络节点数目还大！")
        nodelist = list()  # 缓存节点列表
        centrality = self.centrality(type=type)  # 缓存中心度词典
        for node in centrality:  # 遍历
            nodelist.append((node, centrality[node]))
        nodelist.sort(key=lambda x: x[1], reverse=True)  # 排序
        if not return_value:  # 去除中心度值
            nodelist = [item[0] for item in nodelist]
        return nodelist[:n]  # 返回前n个结果

    def z_score(self):
        """计算节点在社区内度数的z-score，请在提取的社区网络中使用此方法"""
        # z-score反应了节点在社区内部的重要性
        import math
        z = dict()
        def aver(l):
            return sum(l)/len(l)
        degree_dict ={item[0]: item[1] for item in nx.degree(self.network, weight="weight")}
        degree_list = [degree_dict[node] for node in degree_dict]
        degree2_list = [degree * degree for degree in degree_list]
        for node in self.nodes():
            z_numerator = degree_dict[node]-aver(degree_list)
            z_denominator = math.sqrt(aver(degree2_list)-aver(degree_list) * aver(degree_list))
            if z_denominator == 0:
                z[node] = 0
            else:
                z[node] = z_numerator/z_denominator
        return z

    def draw_network(self, layout="spring"):
        """将网络可视化输出"""
        import math
        if self.scale > 300:  # 对于太大的网络，可视化意义不大且效率极低，故只对小型网络进行可视化
            print("网络规模太大，不支持可视化！请抽取更小的子网络进行可视化")
            return
        g = self.network
        node_labels = dict()  # 节点标签
        if layout == 'spring':  # 分散布局
            pos = nx.spring_layout(g, k=2 / math.sqrt(g.number_of_nodes()), iterations=100)
        elif layout == 'shell':  # 环形布局，中间是中心点
            center = [item[0] for item in self.find_nodes_by_centrality(type='degree', n=1)]
            pos = nx.shell_layout(self.network, nlist=[center, [item for item in g.nodes if item not in center]])
            node_labels[center[0]] = center[0].ti
        elif layout == 'spectral':  # 谱状布局，中间是中心点
            pos = nx.spectral_layout(self.network)
        else:
            raise ValueError("没有这种布局！")
        '''以下只是针对测试数据的一种可视化形式！
        实际还需根据B模块的数据格式调整'''
        node_colors = [(item.py - 1969) / 31 for item in g.nodes]
        node_sizes = [math.log2(item[1] + 1) * 20 + 1 for item in g.degree()]
        nx.draw_networkx_edges(g, pos, edge_color='#000000', width=1, with_labels=False, alpha=0.5)
        nx.draw_networkx_nodes(g, pos, node_color=node_colors, with_labels=False, node_size=node_sizes,
                               cmap=plt.cm.Reds, alpha=1, linewidths=0.5, edgecolors='k')
        nx.draw_networkx_labels(g, pos, labels=node_labels, font_size=10, font_color='#FFFFFF')
        # nx.draw(g, pos, nodelist = klist, node_color='b', edge_color=colors,
        #        width=4, edge_cmap=plt.cm.Reds, with_labels=False, node_size = 100, alpha = 0.5)
        plt.show()

    def draw_degree_distribution(self, percentage=False):
        """展示网络的度分布"""
        import math
        import linear_regression
        plt.figure(figsize=(8, 4))
        degree_list = [item[1] for item in self.network.degree]  # network.degree返回节点度数列表,每个元素为(节点,度数)二元组
        degree_set = set(degree_list)  # 后续对相同度数的节点计数用
        if percentage:  # 显示被引量为x的文章数的百分数
            degree_time_list = [(degree, degree_list.count(degree) / self.scale) for degree in degree_set]
        else:
            degree_time_list = [(degree, degree_list.count(degree)) for degree in degree_set]
        degree_time_list.sort(key=lambda i: i[0])  # 排序好的被引量list，第一个元素为被引量，第二个元素为对应被引量的文章数
        x = [math.log2(item[0] + 0.1) for item in degree_time_list]  # 将参数取双对数
        y = [math.log2(item[1]) for item in degree_time_list]
        data = [[a, b] for (a, b) in zip(x, y) if 2 <= a <= 6]
        [b, m] = linear_regression.Linear_regression(data)  # 用线性回归拟合的直线
        x_ = [2, 6]
        y_ = [2 * m + b, 6 * m + b]
        plt.plot(x_, y_, "c", linewidth=4, alpha=0.85, label="α=" + str(-m))
        plt.scatter(x, y, c="m", label="total citation")
        plt.xlabel("degree")
        if percentage:
            plt.ylabel("percentage")
            plt.title("degree distribution in percentage")
        else:
            plt.ylabel("number(log)")
            plt.title("degree distribution(log)")
        plt.legend()
        plt.show()  # 显示图


class CitationNetwork(_DiNetwork):
    def __init__(self, data, from_external=True):
        """data为来自 B 数据处理模块加工过的网络或内部子网,from_external确定数据是外部还是内部"""
        super().__init__()
        if from_external:
            self.network = nxds.read_graph(data)[data]
            self.attribute = self.network.graph  # 还需根据data的数据结构而定
        else:
            self.network = data
        self.scale = self.network.number_of_nodes()
        self.size = self.network.number_of_edges()
        if self.scale:
            self.aver_degree = 2 * self.size / self.scale
        else:
            self.aver_degree = 0
        self.density = nx.density(self.network)
        self._edge_weight = None  # 引文网络无边权

    def connectivity(self, type='node'):
        """计算网络最大主成分的连通度，type请选择node或edge"""
        if type == 'node':
            func = nx.node_connectivity
        elif type == 'edge':
            func = nx.edge_connectivity
        else:
            raise ValueError("输入类型不正确！type请输入node或edge！")
        if not self._connectivity[type]:
            self._connectivity[type] = func(self.extract_max_component().network)
        return self._connectivity[type]

    def extract_nonisolated_network(self):
        """删除网络中的孤立点，返回一个Network对象"""
        filter_iter = nx.isolates(self.network)  # 筛选出的孤立点，格式是迭代器
        filter_list = list()  # 将迭代器转换成list
        for node in filter_iter:  # 将迭代器转换成list
            filter_list.append(node)
        tmp = self.network  # 缓存
        tmp.remove_nodes_from(filter_list)  # 删除节点
        return CitationNetwork(tmp, from_external=False)

    def extract_ego_network(self, node, radius=1):
        """抽取node的个体网或局域网，步长为radius，即包含与node距离在radius内的节点"""
        if node not in self.network.nodes:  # 检测节点不在网络里的异常
            raise ValueError("节点不在网络里！")
        ego_n = nx.ego_graph(self.network, node, radius, True, True, None)
        return CitationNetwork(ego_n, False)

    def extract_subgraph(self, nodes):
        """抽取包含给定节点的子网络"""
        n = self.network.subgraph(nodes)
        return CitationNetwork(n, from_external=False, from_file=False)

    def extract_max_component(self):
        """获取网络的最大主成分"""
        if nx.is_weakly_connected(self.network):
            return CitationNetwork(self.network, from_external=False)  # 如果网络是有向且弱连通的，那它自己就是最大主成分
        else:
            max_comp = None  # 最大主成分
            a = nx.weakly_connected_component_subgraphs(self.network)
            for i in a:
                if max_comp:  # 循环遍历，寻找包含节点最多的成分
                    if i.number_of_nodes() > max_comp.number_of_nodes():
                        max_comp = i
                else:
                    max_comp = i
            return CitationNetwork(max_comp, from_external=False)

    def extract_k_core(self, k=3):
        """抽取网络中的k核，k默认为3"""
        k_core = nx.k_core(self.network, k)
        n_list = list()
        for item in k_core:
            n_list.append(CitationNetwork(item))
        return n_list

    def extract_louvain_community(self):
        """通过Louvain模块化算法抽取网络的社区，返回list，元素为（社区编号，社区对应的Network）"""
        partition = community.best_partition(self.network)
        n_dict = dict()
        for index in set(partition.values()):
            nodelist = [node for node in self.network.nodes() if partition[node] == index]
            n = self.extract_subgraph(nodelist)
            n_dict[index] = CitationNetwork(n, False)
        return n_dict

    def extract_by_attribute(self, key, key_value):
        """根据给定的属性过滤网络"""

        '''还需细化！
        如年份可能根据范围筛选
        本例只给定筛选条件为严格等于'''

        filtered_nodes = list()  # 筛选出符合条件的节点
        for node in self.network.nodes:  # 遍历节点
            if key not in node.attribute:
                raise ValueError("给定的属性不是网络节点的属性！")
            if node.attribute[key] == key_value:  # 实际可能比这要更复杂
                filtered_nodes.append(node)
        if len(filtered_nodes) <= 0:
            print("没有符合条件的节点")
            return None
        else:
            filtered_net = nx.subgraph(self.network, filtered_nodes)  # 过滤后的网络
            return CitationNetwork(filtered_net, False)


class KeywordCooccurrenceNetwork(_Network):
    def __init__(self, data, from_external=False):
        """data为来自 B 数据处理模块加工过的网络或内部子网,from_external确定数据是外部还是内部"""
        super().__init__()
        if from_external:
            self.network = nxds.read_graph(data)[data]
            self.attribute = self.network.graph  # 还需根据data的数据结构而定
        else:
            self.network = data
        self.scale = self.network.number_of_nodes()
        self.size = self.network.number_of_edges()
        if self.scale:
            self.aver_degree = 2 * self.size / self.scale
        else:
            self.aver_degree = 0
        self.density = nx.density(self.network)
        self._edge_weight = 'weight'  # 关键词共现网络有边权

    def connectivity(self, type='node'):
        """计算网络最大主成分的连通度，type请选择node或edge"""
        if type == 'node':
            func = nx.node_connectivity
        elif type == 'edge':
            func = nx.edge_connectivity
        else:
            raise ValueError("输入类型不正确！type请输入node或edge！")
        if not self._connectivity[type]:
            self._connectivity[type] = func(self.extract_max_component().network)
        return self._connectivity[type]

    def extract_nonisolated_network(self):
        """删除网络中的孤立点，返回一个Network对象"""
        filter_iter = nx.isolates(self.network)  # 筛选出的孤立点，格式是迭代器
        filter_list = list()  # 将迭代器转换成list
        for node in filter_iter:  # 将迭代器转换成list
            filter_list.append(node)
        tmp = self.network  # 缓存
        tmp.remove_nodes_from(filter_list)  # 删除节点
        return KeywordCooccurrenceNetwork(tmp, from_external=False)

    def extract_ego_network(self, node, radius=1):
        """抽取node的个体网或局域网，步长为radius，即包含与node距离在radius内的节点"""
        if node not in self.network.nodes:  # 检测节点不在网络里的异常
            raise ValueError("节点不在网络里！")
        ego_n = nx.ego_graph(self.network, node, radius, True, True, None)
        return KeywordCooccurrenceNetwork(ego_n, False)

    def extract_subgraph(self, nodes):
        """抽取包含给定节点的子网络"""
        n = self.network.subgraph(nodes)
        return KeywordCooccurrenceNetwork(n, from_external=False, from_file=False)

    def extract_max_component(self):
        """获取网络的最大主成分"""
        if nx.is_connected(self.network):
            return KeywordCooccurrenceNetwork(self.network, from_external=False)  # 如果网络是无向且连通的，那它自己就是最大主成分
        else:
            max_comp = None  # 最大主成分
            a = nx.connected_component_subgraphs(self.network)
            for i in a:
                if max_comp:  # 循环遍历，寻找包含节点最多的成分
                    if i.number_of_nodes() > max_comp.number_of_nodes():
                        max_comp = i
                else:
                    max_comp = i
            return KeywordCooccurrenceNetwork(max_comp, from_external=False)

    def extract_k_core(self, k=3):
        """抽取网络中的k核，k默认为3"""
        k_core = nx.k_core(self.network, k)
        n_list = list()
        for item in k_core:
            n_list.append(KeywordCooccurrenceNetwork(item))
        return n_list

    def extract_louvain_community(self):
        """通过Louvain模块化算法抽取网络的社区，返回list，元素为（社区编号，社区对应的Network）"""
        partition = community.best_partition(self.network)
        n_dict = dict()
        for index in set(partition.values()):
            nodelist = [node for node in self.network.nodes() if partition[node] == index]
            n = self.extract_subgraph(nodelist)
            n_dict[index] = KeywordCooccurrenceNetwork(n, False)
        return n_dict

    def extract_by_attribute(self, key, key_value):
        """根据给定的属性过滤网络"""

        '''还需细化！
        如年份可能根据范围筛选
        本例只给定筛选条件为严格等于'''

        filtered_nodes = list()  # 筛选出符合条件的节点
        for node in self.network.nodes:  # 遍历节点
            if key not in node.attribute:
                raise ValueError("给定的属性不是网络节点的属性！")
            if node.attribute[key] == key_value:  # 实际可能比这要更复杂
                filtered_nodes.append(node)
        if len(filtered_nodes) <= 0:
            print("没有符合条件的节点")
            return None
        else:
            filtered_net = nx.subgraph(self.network, filtered_nodes)  # 过滤后的网络
            return KeywordCooccurrenceNetwork(filtered_net, False)


# 以下两个测试函数需要prettytable包支持（格式化输出文本用）


def test_citationnetwork(data):
    """测试引文网络"""
    from prettytable import PrettyTable

    n = CitationNetwork(data)
    n3 = n.extract_max_component()
    print("scale:", n3.scale)
    print("size:", n3.size)
    print("average degree:", n3.aver_degree)
    print("density:", n3.density)

    '''center = n.find_nodes_by_centrality(type='betweenness', n=1)[0][0]
    n4 = n.extract_ego_network(center, 1)
    center.show_core_metadata()
    n4.draw_network(layout='shell')'''

    t1 = PrettyTable(["标题", "PR值"])
    pr = pagerank(n3)
    prlist = list()
    for node in pr.keys():
        prlist.append([node.ti, pr[node]])
    prlist.sort(key=lambda i: i[1], reverse=True)
    for item in prlist[:10]:
        t1.add_row(item)
    t1.align["标题"] = 'l'
    print(t1)

    t2 = PrettyTable(["标题", "度数中心度"])
    for item in n3.find_nodes_by_centrality(type='degree', n=10):
        t2.add_row([item[0].ti, item[1]])
    t2.align["标题"] = 'l'
    print(t2)

    t3 = PrettyTable(["标题", "介数中心度"])
    for item in n3.find_nodes_by_centrality(type='betweenness', n=10):
        t3.add_row([item[0].ti, item[1]])
    t3.align["标题"] = 'l'
    print(t3)

    t4 = PrettyTable(["标题", "接近中心度"])
    for item in n3.find_nodes_by_centrality(type='closeness', n=10):
        t4.add_row([item[0].ti, item[1]])
    t4.align["标题"] = 'l'
    print(t4)


def test_keywordnetwork(data):
    """测试关键词共现网络"""
    from prettytable import PrettyTable
    n = KeywordCooccurrenceNetwork(data)
    n3 = n.extract_max_component()
    print("scale:", n3.scale)
    print("size:", n3.size)
    print("average degree:", n3.aver_degree)
    print("density:", n3.density)

    t = PrettyTable(["关键词", "PR值"])
    pr = pagerank(n3)
    prlist = list()
    for node in pr.keys():
        prlist.append([node, pr[node]])
    prlist.sort(key=lambda i: i[1], reverse=True)
    for item in prlist[:10]:
        t.add_row(item)
    t.align["关键词"] = 'l'
    print(t)

    t = PrettyTable(["关键词", "度数中心度"])
    for item in n3.find_nodes_by_centrality(type='degree', n=10):
        t.add_row([item[0], item[1]])
    t.align["关键词"] = 'l'
    print(t)

    t = PrettyTable(["关键词", "介数中心度"])
    for item in n3.find_nodes_by_centrality(type='betweenness', n=10):
        t.add_row([item[0], item[1]])
    t.align["关键词"] = 'l'
    print(t)

    t = PrettyTable(["关键词", "接近中心度"])
    for item in n3.find_nodes_by_centrality(type='closeness', n=10):
        t.add_row([item[0], item[1]])
    t.align["关键词"] = 'l'
    print(t)



