# encoding:utf-8
import re
import data_platform.datasource as ds
from data_platform.config import ConfigManager
from data_platform.datasource.science_direct import ScienceDirectDS, ScienceDirectFactory

from pathlib import Path
import os

import re
import textblob
import source as s
import database as db
import algorithm
current_path = Path(os.getcwd())
data_path = current_path / 'data'
xml_path = data_path / 'unprocessed_articles_xml'
config = ConfigManager({
    "init": {
        "location": xml_path
    }
})


#node == "noun" , relation = "co"表示名词的共现关系，暂时只实现这一种，后续的根据需求再增加
#node == "noun" , realtion = "wordnet"表示名词，使用的关系是由wordnet得到的词语在wordnet中的相似性
def relation_extraction_text(source, document, node, relation, database):
    text = s.search_text(source, document)
    if node == "noun" and relation == "co":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_noun_co(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                #relation_struct = db.search_word_relation(node1_key,node2_key, database)
                relation_struct_ori = db.search_word_relation(node1_key,node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "noun_phrase" and relation == "co":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_noun_phrase_co(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "keyword" and relation == "co":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_keyword_co(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "verb" and relation == "co":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_verb_co(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "adj" and relation == "co":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_adj_co(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "ner" and relation == "co":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_ner_co(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "noun" and relation == "wordnet":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_noun_wordnet(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['similarity'] = r[3]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "adj" and relation == "wordnet":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_adj_wordnet(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['similarity'] = r[3]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "verb" and relation == "wordnet":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_verb_wordnet(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['similarity'] = r[3]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    if node == "keyword" and relation == "wordnet":
        for a in text:
            all_text = a['text']
            relation = algorithm.extract_relation_keyword_wordnet(all_text)
            for r in relation:
                node1_key = "word_" + r[0]
                node2_key = "word_" + r[1]
                relation_struct_ori = db.search_word_relation(node1_key, node2_key, database)
                if relation_struct_ori:
                    relation_struct = relation_struct_ori.values()
                    relation_struct = list(relation_struct)[0]
                else:
                    relation_struct = {}
                if relation_struct:
                    relation_struct['count'] += 1
                    db.update_word_relation(node1_key, node2_key, relation_struct, database)
                else:
                    relation_struct['relation'] = r[2]
                    relation_struct['similarity'] = r[3]
                    relation_struct['count'] = 1
                    db.insert_word_relation(node1_key, node2_key, relation_struct, database)
    return 0


def relation_extraction_paper(source, document, relation, database):
    all = s.search_all(source, document)
    if relation == "cite":
        for a in all:
            node1_doc_doi = "paper_" + str(a['doc_doi'])
            node1_title = a['title']
            for key,value in a['bib_detail'].items():
                if ('doi' in value.keys()):
                    node2_doc_doi = "paper_" + value['doi']
                    relation_struct = {}
                    relation_struct['node1_title'] = node1_title
                    relation_struct['relation'] = "cite"
                    if 'title' in value.keys():
                        if ('maintitle' in value['title'].keys()):
                            relation_struct['node2_title'] = value['title']['maintitle']
                    else:
                        relation_struct['node2_title'] = "null"
                    db.insert_paper_relation(node1_doc_doi,node2_doc_doi,relation_struct,database)

    return 0

#relation = "all"此时暂时实现all，表示抽取共著和引用关系的作者
def relation_extraction_author(source, document, relation, database):
    all = s.search_all(source, document)
    if relation == "all":
        for a in all:
            node1_author = a['author_list']
            if len(node1_author) > 1:
                for i in range(0, len(node1_author)-1):
                    for j in range(i+1, len(node1_author)):
                        node1 = "author_" + node1_author[i]
                        node2 = "author_" + node1_author[j]
                        relation_struct_ori = db.search_author_relation(node1, node2, database)
                        if relation_struct_ori:
                            relation_struct = relation_struct_ori.values()
                            relation_struct = list(relation_struct)[0]
                        else:
                            relation_struct = {}
                        if relation_struct:
                            if relation_struct['relation'] == "co":
                                relation_struct['co_count'] += 1
                                db.update_author_relation(node1, node2, relation_struct, database)
                            elif relation_struct['relation'] == "cite":
                                relation_struct['co_count'] = 1
                                relation_struct['relation'] = "co_cite"
                                db.update_author_relation(node1, node2, relation_struct, database)
                            else:
                                relation_struct['co_count'] += 1
                                db.update_author_relation(node1, node2, relation_struct, database)
                        else:
                            relation_struct['co_count'] = 1
                            relation_struct['relation'] = "co"
                            db.insert_author_relation(node1, node2, relation_struct, database)
            node2_author = []
            for key, value in a['bib_detail'].items():
                if ('authors' in value.keys()):
                    author_names = value['authors']
                    for each in author_names:
                        if ('given-name' in each.keys() and 'surname' in each.keys()):
                            author_name = each['given-name'] + each['surname']
                        else:
                            if ('given-name' in each.keys()):
                                author_name = each['given-name']
                            else:
                                if ('surname' in each.keys()):
                                    author_name = each['surname']
                                else:
                                    author_name = ""
                        node2_author.append(author_name)
            if len(node1_author) > 0 and len(node2_author) > 0:
                for i in range(0, len(node1_author)):
                    for j in range(0, len(node2_author)):
                        node1 = "author_" + node1_author[i]
                        node2 = "author_" + node2_author[j]
                        relation_struct_ori = db.search_author_relation(node1, node2, database)
                        if relation_struct_ori:
                            relation_struct = relation_struct_ori.values()
                            relation_struct = list(relation_struct)[0]
                        else:
                            relation_struct = {}
                        #print(relation_struct)
                        if relation_struct:
                            if relation_struct['relation'] == "co":
                                relation_struct['cite_count'] = 1
                                relation_struct['relation'] = "co_cite"
                                db.update_author_relation(node1, node2, relation_struct, database)
                            elif relation_struct['relation'] == "cite":
                                relation_struct['cite_count'] += 1
                                db.update_author_relation(node1, node2, relation_struct, database)
                            else:
                                relation_struct['cite_count'] += 1
                                db.update_author_relation(node1, node2, relation_struct, database)
                        else:
                            relation_struct['cite_count'] = 1
                            relation_struct['relation'] = "cite"
                            db.insert_author_relation(node1, node2, relation_struct, database)
    return 0


#relation = "paper_author"
def relation_extraction_paper_author(source, document, relation, database):
    all = s.search_all(source, document)
    if relation == "paper_author":
        for a in all:
            node1_doc_doi = "paper_" + str(a['doc_id'])
            node2_authors = a['author_list']
            num = 0
            for i in node2_authors:
                num += 1
                node2_author = "author_" + i
                relation_struct = {}
                relation_struct['relation'] = "paper_author"
                relation_struct['order'] = i
                db.insert_paper_author_relation(node1_doc_doi, node2_author, relation_struct, database)
    return 0


#relation = "paper_word"
def relation_extraction_paper_word(source, document, relation, database):
    all = s.search_all(source, document)
    if relation == "paper_word":
        for a in all:
            node1_doc_doi = "paper_" + str(a['doc_id'])
            text = a['text']
            words = algorithm.extract_word_freq(text)
            for word in words:
                node2_word = "word_" + word
                relation_struct = {}
                relation_struct['relation'] = "paper_word"
                relation_struct['frequency'] = words[word]
                db.insert_paper_author_relation(node1_doc_doi, node2_word, relation_struct, database)
    return 0

#if __name__ == '__main__':
    #relation_extraction_author("ScienceDirectDataSource","1-10","all","knowledge4")
    #经过测试可用！
