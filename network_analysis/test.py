import networkx as nx
import network_analysis.network as network


def test_author_network(data):
    """测试引文网络"""

    n = network.Net(data, net_type='author citation network', weight_type='cite_count')
    n1 = n.extract_max_component()
    print("scale:", n1.scale)
    print("size:", n1.size)
    print("average degree:", n1.aver_degree)
    print("density:", n1.density)
    print()
    names = nx.get_node_attributes(n.network, 'name')
    for item in n1.find_nodes_by_centrality(c_type='degree', n=10):
        print(names[item[0]], round(item[1], 2))
    print()
    # center = n.find_nodes_by_centrality(c_type='degree', n=1)[0][0]
    # n2 = n.extract_ego_network(center, 1)
    n1.draw_network(layout='force')


def test_text_network(data):
    """测试引文网络"""

    n = network.Net(data, net_type='co-word network', weight_type='count')
    n1 = n.extract_max_component()
    print("scale:", n1.scale)
    print("size:", n1.size)
    print("average degree:", n1.aver_degree)
    print("density:", n1.density)
    print()
    # names = nx.get_node_attributes(n.network, 'word')
    # for item in n1.find_nodes_by_centrality(c_type='degree', n=10):
    #     print(names[item[0]], round(item[1],2))
    print()
    # center = n.find_nodes_by_centrality(c_type='degree', n=1)[0][0]
    # n2 = n.extract_ego_network(center, 1)
    n1.draw_network(layout='force')


if __name__ == '__main__':
    test_author_network('knowledge_author_large.graphml')
