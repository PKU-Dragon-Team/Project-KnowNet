# coding=utf-8

import os
import math
from pathlib import Path
from typing import Any, Dict, Text

import networkx as nx
import community
import matplotlib.pyplot as plt
from pyecharts import Graph
from network_analysis.linear_regression import linear_regression

# 以下为系统中使用
from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS

# NET_TYPE = ['none', 'text', 'author', 'paper']


class Net:

    # 以下是初始化就会计算好的属性
    network = None              # 存储网络数据，格式为networkx
    scale = 0                   # 网络的规模，即节点数
    size = 0                    # 网络的大小，即边数
    aver_degree = 0             # 网络的度均值（忽略入度和出度的区别）
    density = 0                 # 网络的密度
    attribute: Dict[Text, Any] = {}          # 网络的固有属性，来自 B 数据处理模块
    net_type = 'none'           # 确定网络类型
    weight_type = 'none'       # 确定网络边权类型

    def __init__(self, data, net_type='none', weight_type='none', from_external=True):
        """data为来自 B 数据处理模块加工过的网络或内部子网,from_external确定数据是外部还是内部"""
        def set_nxds():
            current_location = Path(os.getcwd())
            data_location = current_location / 'data'
            graph_location = data_location / 'graph'
            config = ConfigManager({
                "init": {
                    "location": graph_location
                },
                "file_format": "graphml"
            })
            return NetworkXDS(config)
        nxds = set_nxds()       # 读取网络用模块
        if from_external:
            try:
                self.network = nxds.read_graph(data[:-8])[data[:-8]]
            except ValueError:
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
        self.net_type = net_type
        self.weight_type = weight_type
        self._init_cent()

    def _init_cent(self):
        # 以下是初次调用才会计算的属性，以减少不必要的计算，调用时请使用对应的方法
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

    # 以下是基本属性方法
    def nodes(self, data=False):
        """返回节点列表"""
        return self.network.nodes(data=data)

    def edges(self, data=False):
        """返回边列表"""
        return self.network.edges(data=data)

    def adjacent_matrix(self):
        """将网络转换成numpy邻接矩阵,返回值是numpy矩阵"""
        return nx.to_numpy_matrix(self.network, dtype=int)

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
                if self.weight_type:
                    weight = [edge[2][self.weight_type] for edge in self.network.edges(data=True)]
                    s = 1.0 / sum(weight)
                else:
                    s = 1.0 / (len(self.network) - 1.0)
                self._centrality[c_type] = {n: d * s for n, d in self.network.degree(weight=self.weight_type)}
            elif c_type == 'indegree':
                s = 1.0 / (len(self.network) - 1.0)
                self._centrality[c_type] = {n: d * s for n, d in self.network.in_degree(weight=self.weight_type)}
            elif c_type == 'outdegree':
                s = 1.0 / (len(self.network) - 1.0)
                self._centrality[c_type] = {n: d * s for n, d in self.network.out_degree(weight=self.weight_type)}
            elif c_type == 'eigenvector':
                self._centrality[c_type] = nx.eigenvector_centrality(self.network, max_iter=1000,
                                                                     weight=self.weight_type)
            elif c_type == 'katz':
                self._centrality[c_type] = nx.katz_centrality(self.network, max_iter=1000, weight=self.weight_type)
            elif c_type == 'pagerank':
                pr = nx.pagerank(self.network, weight=self.weight_type)
                self._centrality[c_type] = {node: pr[node] for node in pr}
            elif c_type == 'betweenness':
                self._centrality[c_type] = nx.betweenness_centrality(self.network, weight=self.weight_type)
            elif c_type == 'closeness':
                self._centrality[c_type] = nx.closeness_centrality(self.network)
        return self._centrality[c_type]

    def node_centrality(self, node, c_type='degree'):
        return self.centrality(c_type=c_type)[node]

    # def centralization(self, c_type='degree'):
    #     if c_type == 'degree':
    #         if not self._centralization['degree']:
    #             1  # 占位符
    #             # self.centralization['degree'] = nx.degree_centrality(self.network)        # 中心势计算之后补充
    #         return self._centralization
    #     elif c_type == 'betweenness':
    #         if not self._centralization['betweenness']:
    #             1  # 占位符
    #             # self.centralization['betweenness'] = nx.betweenness_centrality(self.network)
    #         return self._centralization
    #     elif c_type == 'closeness':
    #         if not self._centralization['closeness']:
    #             1  # 占位符
    #             # self.centralization['closeness'] = nx.closeness_centrality(self.network)
    #         return self._centralization
    #     else:
    #         raise ValueError("输入类型不正确！type请输入degree或betweenness或closeness！")

    def find_nodes_by_centrality(self, c_type='degree', n=-1, return_value=True):
        """根据中心性抽取重要节点，n为抽取的节点个数, -1表示获取所有值
        return_value决定返回值为节点列表还是(节点，中心度)元组列表"""
        if n > self.scale:
            n = self.scale
        nodelist = list()  # 缓存节点列表
        cent = self.centrality(c_type=c_type)  # 缓存中心度词典
        for node in cent:  # 遍历
            nodelist.append((node, cent[node]))
        nodelist.sort(key=lambda x: x[1], reverse=True)  # 排序
        if not return_value:  # 去除中心度值
            nodelist = [item[0] for item in nodelist]
        if n < 0:
            return nodelist      # 返回所有结果
        else:
            return nodelist[:n]  # 返回前n个结果

    # 以下是可视化输出的方法
    def draw_network(self, layout="force"):
        """将网络可视化输出"""
        if self.scale > 10000:  # 对于太大的网络，可视化意义不大且效率极低，故只对小型网络进行可视化
            print("网络规模太大("+str(self.scale)+")，不支持可视化！请抽取更小的子网络进行可视化")
            return
        g = self.network
        partition = community.best_partition(g)
        if layout.lower() != 'force' and layout.lower() != 'circular':
            raise ValueError("没有这种布局！布局请选择force或circular")
        # 获取节点名称映射
        names = nx.get_node_attributes(g, 'name')
        nodes = [{'name': names[n], 'symbolSize': math.log2(nx.degree(g, n, weight=self.weight_type)+1),
                  'category': partition[n]}
                 for n in g.nodes()]
        links = [{'source': names[e[0]], 'target': names[e[1]], 'value': e[2][self.weight_type]} for e in g.edges]
        graph = Graph(self.net_type, width=1200, height=750)
        graph.add(
            "",
            nodes,
            links,
            categories=list(set(partition.values())),
            label_pos="right",
            graph_repulsion=50,
            graph_layout=layout,
            is_legend_show=False,
            line_curve=0.2,
            label_text_color=None,
        )
        graph.render(self.net_type+'.html')

    def draw_degree_distribution(self, percentage=False):
        """展示网络的度分布"""
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
        [b, m] = linear_regression(data)  # 用线性回归拟合的直线
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
        [b, m] = linear_regression(data)  # 用线性回归拟合的直线
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
        [b, m] = linear_regression(data)  # 用线性回归拟合的直线
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

    # 以下是抽取子网络的方法
    def extract_nonisolated_network(self):
        """删除网络中的孤立点，返回一个Network对象"""
        filter_iter = nx.isolates(self.network)  # 筛选出的孤立点，格式是迭代器
        filter_list = list()  # 将迭代器转换成list
        for node in filter_iter:  # 将迭代器转换成list
            filter_list.append(node)
        tmp = self.network  # 缓存
        tmp.remove_nodes_from(filter_list)  # 删除节点
        return Net(tmp, self.net_type, self.weight_type, from_external=False)

    def extract_ego_network(self, node, radius=1):
        """抽取node的个体网或局域网，步长为radius，即包含与node距离在radius内的节点"""
        if node not in self.network.nodes:  # 检测节点不在网络里的异常
            raise ValueError("节点不在网络里！")
        ego_net = nx.ego_graph(self.network, node, radius, True, True, None)
        return Net(ego_net, self.net_type, self.weight_type, from_external=False)

    def extract_subgraph(self, nodes):
        """抽取包含给定节点的子网络"""
        net = self.network.subgraph(nodes)
        return Net(net, self.net_type, self.weight_type, from_external=False)

    def extract_max_component(self):
        """获取网络的最大主成分"""
        print(self.network)
        if nx.is_directed(self.network) and nx.is_weakly_connected(self.network):
            return self  # 如果网络是有向且弱连通的，那它自己就是最大主成分
        if not nx.is_directed(self.network) and nx.is_connected(self.network):
            return self  # 如果网络是无向且连通的，那它自己就是最大主成分
        max_comp = None  # 最大主成分
        if nx.is_directed(self.network):
            # 如果是有向的
            a = nx.weakly_connected_component_subgraphs(self.network)
        else:
            # 如果是无向的
            a = nx.connected_component_subgraphs(self.network)
        for i in a:
            if max_comp:  # 循环遍历，寻找包含节点最多的成分
                if i.number_of_nodes() > max_comp.number_of_nodes():
                    max_comp = i
            else:
                max_comp = i
        return Net(max_comp, self.net_type, self.weight_type, from_external=False)

    def extract_k_cores(self, k=3):
        """抽取网络中的k核，k默认为3"""
        k_core = nx.k_core(self.network, k)
        n_list = list()
        for item in k_core:
            n_list.append(Net(item, self.net_type, self.weight_type, from_external=False))
        return n_list

    def extract_louvain_communities(self):
        """通过Louvain模块化算法抽取网络的社区，返回list，元素为（社区编号，社区对应的Network）"""
        partition = community.best_partition(self.network)
        n_list = list()
        for index in sorted(list(set(partition.values()))):
            nodelist = [node for node in self.network.nodes() if partition[node] == index]
            n = self.extract_subgraph(nodelist)
            n_list.append(n)
        return n_list

    def extract_by_attribute(self, key, key_value):
        """根据给定的属性过滤网络"""

        # 还需改进
        # 如年份可能根据范围筛选,本例只给定筛选条件为严格等于'''

        filtered_nodes = list()  # 筛选出符合条件的节点
        for node in self.network.nodes(data=True):  # 遍历节点
            if key not in node:
                raise ValueError("给定的属性不是网络节点的属性！")
            if node[key] == key_value:  # 实际可能比这要更复杂
                filtered_nodes.append(node)
        if filtered_nodes:
            print("没有符合条件的节点")
            return None
        filtered_net = nx.subgraph(self.network, filtered_nodes)  # 过滤后的网络
        return Net(filtered_net, self.net_type, self.weight_type, from_external=False)
