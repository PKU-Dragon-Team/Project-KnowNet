
from network_analysis.network import *


def test_author_network(data):
    """测试引文网络"""

    n = AuthorNet(data)
    n1 = n.extract_max_component()
    print("scale:", n1.scale)
    print("size:", n1.size)
    print("average degree:", n1.aver_degree)
    print("density:", n1.density)

    for item in n1.find_nodes_by_centrality(c_type='degree', n=10):
        print(item[0], item[1])

    center = n.find_nodes_by_centrality(c_type='degree', n=1)[0][0]
    n2 = n.extract_ego_network(center, 1)
    n2.draw_network(layout='shell')
