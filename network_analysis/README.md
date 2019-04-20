# C-网络分析模块(network_analysis) tutorial

## 功能
1.	从图数据库中读取网络数据并解析（解析为networkx-Graph等格式）。
2.	对解析的网络抽取满足特定条件的子网络，以供选择性分析与对比性分析之用。
3.	对解析的网络或抽取的子网络的参数进行计算。
4.	对解析的网络或抽取的子网络的参数、网络进行可视化。

---

## 分析的基础——`Net`对象
C模块的一切分析属性和方法全部封装在`network.py`文件的`Net`类中，在开始分析前，首先要从图数据库中读取B模块建构好的网络，并转换成`Net`对象，以进行后续分析，`Net`对象的初始化方式为：
```
Net(data, net_type='none', weight_type='none', from_external=True)
```
初始化时，B模块会为C模块提供网络在图数据库的索引`data`，网络类型`net_type`，边权类型`weight_type`。C模块建构好`Net`网络，即可开始分析。如：
```
n = Net('test.graphml', net_type='author citation network', weight_type='cite_count')
```
`Net`对象存储了网络的全部内容，并封装了网络分析的基本属性、可视化方法和网络抽取方法和其他常用分析方法。这四者是`Net`对象的基本功能。

>注：网络本体以`networkx.Graph`或`networkx.DiGraph`的格式存储在`network`属性中，若需要扩展Net类的属性和方法，可调取network属性存储的网络。

## 网络基本属性
Net对象的属性有三类：
1. 网络本体及其基本属性。包括网络本体`network`、网络属性`attribute`、网络类型`net_type`、边权类型`weight_type`。
2. 创建时计算好的网络属性。包括节点数`scale`、边数`size`、平均点度数`aver_degree`、密度`density`。
3. 在需要时在计算的属性，作为方法被调用，第一次计算后存储在内部属性中，之后再次调用时不必再计算。包括连通性`_connectivity`，中心性`_centrality`。这类属性需通过方法调用，即`Net.connectivity`、`Net.centrality`。
使用方法如下
```
a = n.network
b = n.scale
c = n.centrality()
```
## 可视化方法
Net对象可实现下述可视化方法：
1. `draw_network(layout="force", render=False)`：绘制网络本体，`layout`确定其布局方式（`force`为力导向布局，建议使用；`circular`为环形布局），`render`确定是否在调用时直接渲染到屏幕。不管是否直接渲染，该方法都将返回网络的可视化数据格式，此格式基于`pyecharts`的`Graph`类，详细用法请参见[pyecharts-Graph文档](http://pyecharts.org/#/zh-cn/charts_base?id=graph%EF%BC%88%E5%85%B3%E7%B3%BB%E5%9B%BE%EF%BC%89)。
2. `draw_degree_distribution(percentage=False)` ：绘制网络点度数分布，直接通过`matplotlib.pyplot`绘制到屏幕。此方法为可视化调试用，结果一般来说符合长尾分布。`percentage`确定纵坐标使用绝对度数还是度数占总度数的百分比。
3. `draw_indegree_distribution(percentage=False)`； `draw_outdegree_distribution(percentage=False)`：绘制入度和出度分布，不赘述。
>注：网络可使用的统计分析图表很多，可以使用`matplotlib.pyplot`，也可以使用`pycharts`，后续可参考上述①②两方法的内部结构对可视化方法进行扩展，或参阅两个可视化包的文档。[Matplotlib官方文档](https://matplotlib.org/index.html)。

## 网络抽取方法
`Net`对象可抽取自身的子网络，以供进一步分析或对比分析。抽取子网时，又分为抽取单个子网、抽取多个子网。
1. 抽取单个子网：`extract_nonisolated_network`; `extract_ego_network`; `extract_subgraph`; `extract_max_component`; `extract_by_attribute` 。以上方法对应的子网是唯一的，经过处理后，建构出唯一新的`Net`对象并返回。
2. 抽取多个子网：`extract_k_cores`; `extract_louvain_communities`。以上方法能够抽取出多个子网，因此得到的结果为`list`，每个元素都是新建构的`Net`对象。

## 其他常用分析方法
还有一些常用的网络分析方法，单独封装，例如：
1. `node_centrality(node, c_type='degree')`：查询某个节点的中心度。
2. `find_nodes_by_centrality(c_type='degree', n=-1, return_value=True)`：查询中心性最高的前`n`个节点。因为分析时往往关注重要的节点，用此方法可以找出重要的节点。`n=-1`时，返回所有节点（按中心度排序）。`return_value`决定返回值是否包括节点的中心度值。
