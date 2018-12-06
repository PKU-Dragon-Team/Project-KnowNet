# encoding:utf-8
from pathlib import Path
import os
from data_platform.config import ConfigManager
import node as nd
import relation as rela

current_path = Path(os.getcwd())
data_path = current_path / 'data'
xml_path = data_path / 'unprocessed_articles_xml'
config = ConfigManager({
    "init": {
        "location": xml_path
    }
})


# node = noun verb adj noun_phrase keyword ner; relation = co wordnet
# please don't use wordnet now!!! it's too slow
def create_network_text(source, document, node, relation, database):
    nd.node_extraction_text(source, document, node, database)
    rela.relation_extraction_text(source, document, node, relation, database)
    return 0


# relation = all including co-author and cite relation and coANDcite
def create_network_author(source, document, relation, database):
    nd.node_extraction_author(source, document, database)
    rela.relation_extraction_author(source, document, relation, database)
    return 0


# relation = cite
def create_network_paper(source, document, relation, database):
    nd.node_extraction_paper(source, document, database)
    rela.relation_extraction_paper(source, document, relation, database)
    return 0


# elation = paper_author OR paper_word
def create_other(source, document, relation, database):
    if relation == "paper_author":
        rela.relation_extraction_paper_author(source, document, relation, database)
    if relation == "paper_word":
        rela.relation_extraction_paper_word(source, document, relation, database)
    return 0

# if __name__ == '__main__':
# create_other("ScienceDirectDataSource","1-10","paper_word","knowledge6")
