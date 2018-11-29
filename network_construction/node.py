# encoding:utf-8
import os
from pathlib import Path
from data_platform.config import ConfigManager
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


# the output format is a dictionary; its key is node_key and the properties are id name email;
# if there is nop author-name, the key is author_null
def node_extraction_author(source, document, database):
    authors = s.search_author(source, document)
    citations = s.search_citation(source, document)
    for a in authors:
        author_name = a['author_list'][0]
        node_key = "author_" + author_name
        node_struct = {}
        node_struct['id'] = "null"
        node_struct['name'] = author_name
        node_struct['email'] = "null"
        db.insert_author(node_key, node_struct, database)
    for c in citations:
        for value in c['bib_detail'].items():
            if 'authors' in value.keys():
                author_names = value['authors']
                for each in author_names:
                    if 'given-name' in each.keys() and 'surname' in each.keys():
                        author_name = each['given-name'] + each['surname']
                    else:
                        if 'given-name' in each.keys():
                            author_name = each['given-name']
                        else:
                            if 'surname' in each.keys():
                                author_name = each['surname']
                            else:
                                author_name = "null"
                    node_key = "author_" + author_name
                    node_struct = {}
                    node_struct['id'] = "null"
                    node_struct['name'] = author_name
                    node_struct['email'] = "null"
                    db.insert_author(node_key, node_struct, database)
    return 0


# if we can not get a property; the default value is "null"
# for all the citation papers, if there is no bib_number property, the default number is -1
def node_extraction_paper(source, document, database):
    all_ = s.search_all(source, document)
    citations = s.search_citation(source, document)
    for a in all_:
        doc_doi = a['doc_doi']
        node_key = "paper_" + doc_doi
        node_struct = {}
        node_struct['doc_doi'] = doc_doi
        node_struct['title'] = a['title']
        node_struct['author_number'] = a['author_number']
        node_struct['bib_number'] = a['bib_number']
        db.insert_paper(node_key, node_struct, database)
    for c in citations:
        for value in c['bib_detail'].items():
            if 'doi' in value.keys():
                docdoi = value['doi']
                node_key = "paper_" + docdoi
                node_struct = {}
                node_struct['doc_doi'] = docdoi
                if 'title' in value.keys():
                    if 'maintitle' in value['title'].keys():
                        node_struct['title'] = value['title']['maintitle']
                    else:
                        node_struct['title'] = "null"
                else:
                    node_struct['title'] = "null"
                node_struct['author_number'] = len(value['authors'])
                node_struct['bib_number'] = -1
                db.insert_paper(node_key, node_struct, database)
    return 0


# the "node" argument's value can be "noun"/"adj"/"verb"/"noun_phrase"/"keyword"/"ner"
def node_extraction_text(source, document, node, database):
    text = s.search_text(source, document)
    if node == "noun":
        for a in text:
            all_text = a['text']
            words = algorithm.extract_noun(all_text)
            for w in words:
                node_key = "word_" + w
                node_struct = {}
                node_struct['word'] = w
                db.insert_word(node_key, node_struct, database)
    if node == "adj":
        for a in text:
            all_text = a['text']
            words = algorithm.extract_adj(all_text)
            for w in words:
                node_key = "word_" + w
                node_struct = {}
                node_struct['word'] = w
                db.insert_word(node_key, node_struct, database)
    if node == "keyword":
        for a in text:
            all_text = a['text']
            words = algorithm.extract_keyword(all_text)
            for w in words:
                node_key = "word_" + w
                node_struct = {}
                node_struct['word'] = w
                db.insert_word(node_key, node_struct, database)
    if node == "noun_phrase":
        for a in text:
            all_text = a['text']
            words = algorithm.extract_noun_phrase(all_text)
            for w in words:
                node_key = "word_" + w
                node_struct = {}
                node_struct['word'] = w
                db.insert_word(node_key, node_struct, database)
    if node == "ner":
        for a in text:
            all_text = a['text']
            words = algorithm.extract_ner(all_text)
            for w in words:
                node_key = "word_" + w
                node_struct = {}
                node_struct['word'] = w
                db.insert_word(node_key, node_struct, database)
    if node == "verb":
        for a in text:
            all_text = a['text']
            words = algorithm.extract_verb(all_text)
            for w in words:
                node_key = "word_" + w
                node_struct = {}
                node_struct['word'] = w
                db.insert_word(node_key, node_struct, database)
    return 0

# if __name__ == '__main__':
# node_extraction_author("ScienceDirectDataSource","1-50","knowledge")
# 此模块经过验证可用，一些常见的异常已经被处理
