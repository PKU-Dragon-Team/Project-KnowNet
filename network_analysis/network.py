# coding=utf-8

import networkx as nx
import community
import matplotlib.pyplot as plt
# 以下为系统中使用
from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS
from pathlib import Path
import os


class _Net:

    # 以下是初始化就会计算好的属性
    network = None              # 存储网络数据，格式为networkx
    scale = 0                   # 网络的规模，即节点数
    size = 0                    # 网络的大小，即边数
    aver_degree = 0             # 网络的度均值（忽略入度和出度的区别）
    density = 0                 # 网络的密度
    attribute = dict()          # 网络的固有属性，来自 B 数据处理模块
    _edge_weight = None         # 确定网络有无边权

    # 以下是初次调用才会计算的属性，以减少不必要的计算，调用时请使用对应的方法
    _connectivity = {"node": None,
                     "edge": None}  # 网络的连通度
    _centrality = {"degree": None,
                   "indegree": None,
                   "outdegree": None,
                   "eigenvector": None,
                   "katz": None,
                   "pagerank": None,
                   "betweenness": None,
                   "closeness": None}  # 网络的节点中心度
    _centralization = {"degree": None,
                       "indegree": None,
                       "outdegree": None,
                       "eigenvector": None,
                       "katz": None,
                       "pagerank": None,
                       "betweenness": None,
                       "closeness": None}  # 网络的中心势

    def __init__(self, data, from_external=True):
        """data为来自 B 数据处理模块加工过的网络或内部子网,from_external确定数据是外部还是内部"""
        # 中心度初始化，否则重复建类时会继承上一个实例的值
        def set_nxds():
            current_location = Path(os.getcwd())
            data_location = current_location / 'data'
            graph_location = data_location / 'graph'
            config = ConfigManager({
                "init": {
                    "location": graph_location
                },
                "config": "graphml"
            })
            return NetworkXDS(config)
        nxds = set_nxds()       # 读取网络用模块
        if from_external:
            try:
                self.network = nxds.read_graph(data[:-8])[data[:-8]]
            except:
                raise ValueError("graph name is not correct!")
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
        self._edge_weight = "weight"

    def nodes(self, data=False):
        """返回节点列表"""
        return self.network.nodes(data=data)

    def edges(self, data=False):
        """返回边列表"""
        return self.network.edges(data=data)

    def connectivity(self, c_type='node'):
        """计算网络最大主成分的连通度，type请选择node或edge"""
        if c_type == 'node':
            func = nx.node_connectivity
        elif c_type == 'edge':
            func = nx.edge_connectivity
        else:
            raise ValueError("输入类型不正确！type请输入node或edge！")
        if not self._connectivity[c_type]:
            self._connectivity[c_type] = func(self.extract_max_component().network)
        return self._connectivity[c_type]

    def centrality(self, c_type='degree'):
        """计算整个网络的所有节点的中心度，返回一个dict"""
        if c_type not in self._centrality.keys():  # 检测输入类型不正确的异常
            raise ValueError(
                "输入类型不正确！type请输入degree/indegree/outdegree/eigenvector/katz/pagerank/betweenness/closeness！")
        if not self._centrality[c_type]:
            if c_type == 'degree':  # 因为networkx的度数中心度计算不带权重，故自制了一个
                if self._edge_weight:
                    weight = [edge[2]['weight'] for edge in self.network.edges(data=True)]
                    s = 1.0 / sum(weight)
                else:
                    s = 1.0 / (len(self.network) - 1.0)
                self._centrality[c_type] = {n: d * s for n, d in self.network.degree(weight=self._edge_weight)}
            elif c_type == 'indegree':
                s = 1.0 / (len(self.network) - 1.0)
                self._centrality[c_type] = {n: d * s for n, d in self.network.in_degree(weight=self._edge_weight)}
            elif c_type == 'outdegree':
                s = 1.0 / (len(self.network) - 1.0)
                self._centrality[c_type] = {n: d * s for n, d in self.network.out_degree(weight=self._edge_weight)}
            elif c_type == 'eigenvector':
                self._centrality[c_type] = nx.eigenvector_centrality(self.network, max_iter=1000,
                                                                     weight=self._edge_weight)
            elif c_type == 'katz':
                self._centrality[c_type] = nx.katz_centrality(self.network, max_iter=1000, weight=self._edge_weight)
            elif c_type == 'pagerank':
                pr = nx.pagerank(self.network, weight=self._edge_weight)
                self._centrality[c_type] = {node: pr[node] for node in pr}
            elif c_type == 'betweenness':
                self._centrality[c_type] = nx.betweenness_centrality(self.network, weight=self._edge_weight)
            elif c_type == 'closeness':
                self._centrality[c_type] = nx.closeness_centrality(self.network)
        return self._centrality[c_type]

    def node_centrality(self, node, c_type='degree'):
        return self.centrality(c_type=c_type)[node]

    def centralization(self, c_type='degree'):
        if c_type == 'degree':
            if not self._centralization['degree']:
                1  # 占位符
                # self.centralization['degree'] = nx.degree_centrality(self.network)        # 中心势计算之后补充
            return self._centralization
        elif c_type == 'betweenness':
            if not self._centralization['betweenness']:
                1  # 占位符
                # self.centralization['betweenness'] = nx.betweenness_centrality(self.network)
            return self._centralization
        elif c_type == 'closeness':
            if not self._centralization['closeness']:
                1  # 占位符
                # self.centralization['closeness'] = nx.closeness_centrality(self.network)
            return self._centralization
        else:
            raise ValueError("输入类型不正确！type请输入degree或betweenness或closeness！")

    def find_nodes_by_centrality(self, c_type='degree', n=1, return_value=True):
        """根据中心性抽取重要节点，n为抽取的节点个数
        return_value决定返回值为节点列表还是(节点，中心度)元组列表"""
        if n > self.scale:
            raise ValueError("n不能比网络节点数目还大！")
        nodelist = list()  # 缓存节点列表
        centrality = self.centrality(c_type=c_type)  # 缓存中心度词典
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
            center = [item[0] for item in self.find_nodes_by_centrality(c_type='degree', n=1)]
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

    @classmethod
    def extract_nonisolated_network(cls):
        """删除网络中的孤立点，返回一个Network对象"""
        filter_iter = nx.isolates(cls.network)  # 筛选出的孤立点，格式是迭代器
        filter_list = list()  # 将迭代器转换成list
        for node in filter_iter:  # 将迭代器转换成list
            filter_list.append(node)
        tmp = cls.network  # 缓存
        tmp.remove_nodes_from(filter_list)  # 删除节点
        return cls(tmp, from_external=False)

    @classmethod
    def extract_ego_network(cls, node, radius=1):
        """抽取node的个体网或局域网，步长为radius，即包含与node距离在radius内的节点"""
        if node not in cls.network.nodes:  # 检测节点不在网络里的异常
            raise ValueError("节点不在网络里！")
        ego_net = nx.ego_graph(cls.network, node, radius, True, True, None)
        return cls(ego_net, False)

    @classmethod
    def extract_subgraph(cls, nodes):
        """抽取包含给定节点的子网络"""
        net = cls.network.subgraph(nodes)
        return cls(net, from_external=False)

    @classmethod
    def extract_max_component(cls):
        """获取网络的最大主成分"""
        if nx.is_directed(cls.network) and nx.is_weakly_connected(cls.network):
            return cls(cls.network, from_external=False)  # 如果网络是有向且弱连通的，那它自己就是最大主成分
        elif not nx.is_directed(cls.network) and nx.is_connected(cls.network):
            return cls(cls.network, from_external=False)  # 如果网络是无向且连通的，那它自己就是最大主成分
        else:
            max_comp = None  # 最大主成分
            if nx.is_directed(cls.network):
                # 如果是有向的
                a = nx.weakly_connected_component_subgraphs(cls.network)
            else:
                # 如果是无向的
                a = nx.connected_component_subgraphs(cls.network)
            for i in a:
                if max_comp:  # 循环遍历，寻找包含节点最多的成分
                    if i.number_of_nodes() > max_comp.number_of_nodes():
                        max_comp = i
                else:
                    max_comp = i
            return cls(max_comp, from_external=False)

    @classmethod
    def extract_k_cores(cls, k=3):
        """抽取网络中的k核，k默认为3"""
        k_core = nx.k_core(cls.network, k)
        n_list = list()
        for item in k_core:
            n_list.append(cls(item, False))
        return n_list

    @classmethod
    def extract_louvain_communities(cls):
        """通过Louvain模块化算法抽取网络的社区，返回list，元素为（社区编号，社区对应的Network）"""
        partition = community.best_partition(cls.network)
        n_dict = dict()
        for index in set(partition.values()):
            nodelist = [node for node in cls.network.nodes() if partition[node] == index]
            n = cls.extract_subgraph(nodelist)
            n_dict[index] = cls(n, False)
        return n_dict

    @classmethod
    def extract_by_attribute(cls, key, key_value):
        """根据给定的属性过滤网络"""

        '''还需细化！
        如年份可能根据范围筛选
        本例只给定筛选条件为严格等于'''

        filtered_nodes = list()  # 筛选出符合条件的节点
        for node in cls.network.nodes:  # 遍历节点
            if key not in node.attribute:
                raise ValueError("给定的属性不是网络节点的属性！")
            if node.attribute[key] == key_value:  # 实际可能比这要更复杂
                filtered_nodes.append(node)
        if len(filtered_nodes) <= 0:
            print("没有符合条件的节点")
            return None
        else:
            filtered_net = nx.subgraph(cls.network, filtered_nodes)  # 过滤后的网络
            return cls(filtered_net, False)


class TextNet(_Net):

    def __init__(self, data, from_external=True):
        super().__init__(data, from_external)


class AuthorNet(_Net):

    def __init__(self, data, from_external=True):
        super().__init__(data, from_external)


class PaperNet(_Net):
    def __init__(self, data, from_external=True):
        super().__init__(data, from_external)
