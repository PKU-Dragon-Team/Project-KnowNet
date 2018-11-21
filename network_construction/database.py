# encoding:utf-8
import re

from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS, GraphValType
from pathlib import Path
import os


def init():
    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        'file_format': 'graphml'
    })
    return NetworkXDS(config)

nxds = init()

def create_database(database_name):
    nxds.create_graph({database_name: {}})


def insert_paper(node_key, node_struct, database_name):
    # node_key is like paper_XXXX
    if nxds.read_node({(database_name, node_key):{}}):
        return 0
    else:
        nxds.create_node({(database_name, node_key):{}}, node_struct)


def insert_author(node_key, node_struct, database_name):
    # node_key is like author_XXXX
    if nxds.read_node({(database_name, node_key):{}}):
        return 0
    else:
        nxds.create_node({(database_name, node_key):{}}, node_struct)


def insert_word(node_key, node_struct, database_name):
    # node_key is like word_XXXX
    if nxds.read_node({(database_name, node_key):{}}):
        return 0
    else:
        nxds.create_node({(database_name, node_key):{}}, node_struct)


def insert_paper_relation(node1_key, node2_key, relation_struct, database_name):
    if nxds.read_edge({(database_name, (node1_key, node2_key)):{}}):
        relation_struct_ori = nxds.read_edge({(database_name, (node1_key, node2_key)):{}})
        relation_struct_new = relation_struct_ori.values()
        relation_struct_new = list(relation_struct_new)[0]
        relation_struct_new['count'] += 1
        nxds.update_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct_new)
    else:
        relation_struct['count'] = 1
        nxds.create_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


def insert_author_relation(node1_key, node2_key, relation_struct, database_name):
    if nxds.read_edge({(database_name, (node1_key, node2_key)):{}}):
        relation_struct_ori = nxds.read_edge({(database_name, (node1_key, node2_key)):{}})
        relation_struct_new = relation_struct_ori.values()
        relation_struct_new = list(relation_struct_new)[0]
        relation_struct_new['count'] += 1
        nxds.update_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct_new)
    else:
        relation_struct['count'] = 1
        nxds.create_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


# Now in the database each paper have only one author. It we can have more than one author,
# then the relation between authors can be "cite" and "cooperate". Then we will need this.
def search_author_relation(node1_key, node2_key, database_name):
        if nxds.read_edge({(database_name, (node1_key, node2_key)):{}}):
            return nxds.read_edge({(database_name, (node1_key, node2_key)):{}})
        else:
            return {}


def update_author_relation(node1_key, node2_key, relation_struct, database_name):
    nxds.update_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


# the functions for word_relation are complicated because word and word can have many kinds of relations
def insert_word_relation(node1_key, node2_key, relation_struct, database_name):
    nxds.create_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


def search_word_relation(node1_key, node2_key, database_name):
    if nxds.read_edge({(database_name, (node1_key, node2_key)):{}}):
        return nxds.read_edge({(database_name, (node1_key, node2_key)):{}})
    else:
        return {}


def update_word_relation(node1_key, node2_key, relation_struct, database_name):
    nxds.update_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


def insert_paper_author_relation(node1_key, node2_key, relation_struct, database_name):
    nxds.create_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


def insert_paper_word_relation(node1_key, node2_key, relation_struct, database_name):
    nxds.create_edge({(database_name, (node1_key, node2_key)):{}}, relation_struct)


#if __name__ == '__main__':
    #create_database("knowledge6")
    #可成功建立数据库
