# network analysis module

功能
1.	从图数据库中读取网络数据并解析（解析为networkx-Graph等格式）。
2.	对解析的网络抽取满足特定条件的子网络，以供选择性分析与对比性分析之用。
3.	对解析的网络或抽取的子网络的参数进行计算。
4.	对解析的网络或抽取的子网络的参数、网络进行可视化。

***-----------------------------------***

更新记录
【11.15】
1. Algorithm模块更改为algorithm
2. Network模块更改为network
3. 合并_Network和_DiNetwork为_Net
4. 去除CitationNetwork和KeywordCooccurrenceNetwork，改为TextNet，AuthorNet，PaperNet
5. 三个具体类的全部函数统一移入父类_Net，以更高度的集成化
6.调整了许多变量命名，使之更规范

【11.22】
1. _Net更改为Net，去除了TextNet，AuthorNet，PaperNet，功能全部集成入Net
2. Net类加入node_type, weight_type，以标志网络类型
3. 基本完成了网络可视化算法

【11.29】
1. Net模块新增adjacent_matrix方法，返回其邻接矩阵
2. 暂时去除了algorithm模块，后续算法直接写入network模块
3. 根据flake8和pylint，将代码规范化

【3.5】
1. 更新了UI模块，可以读取特定的网络，抽取子网络，进行基本分析，对网络可视化
2. 修复了若干BUG

【下一步目标】
多子网络的对比分析