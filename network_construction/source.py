# encoding:utf-8
# import utils.datasource as ds
# import data_platform.document as ds
# import data_platform as dp
# from data_platform.datasource import ScienceDirectDS as ScienceDirectDataSource
# from utils.datasource import OrientDBDataSource
from data_platform.config import ConfigManager
from data_platform.datasource.science_direct import ScienceDirectDS
from pathlib import Path
import os
current_path = Path(os.getcwd())
data_path = current_path / 'data'
xml_path = data_path / 'unprocessed_articles_xml'
config = ConfigManager({
    "init": {
        "location": xml_path
    }
})


def search_author(source, document):
    """source(STRING) is the name of the database; document is a string just like 1-100_300-400"""
    if source == "ScienceDirectDataSource":
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()

    else:
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()
    doc_num = document.split('_')
    author_struct_array = []
    for doc_num_iter in doc_num:
        doc_num_range = doc_num_iter.split('-')
        doc_num_start = doc_num_range[0]
        doc_num_end = doc_num_range[1]
        for i in range(int(doc_num_start), int(doc_num_end)+1):
            if (('_default', str(i)) in docset.keys()):
                doc = docset[('_default', str(i))]
                coredata = doc.metadatas['coredata']
                coredata_dict = coredata.meta_dict
                if('creator' in coredata_dict.keys()):
                    creator = coredata_dict['creator']
                else:
                    creator = 'none'
                author_struct = {}
                author_struct['doc_id'] = i
                if ('doi' in coredata_dict.keys()):
                    author_struct['doc_doi'] = coredata_dict['doi']
                else:
                    author_struct['doc_doi'] = 'none'
                if ('title' in coredata_dict.keys()):
                    author_struct['title'] = coredata_dict['title']
                else:
                    author_struct['title'] = 'none'
                author_struct['author_number'] = 1
                author_struct['author_list'] = [creator]
                author_struct_array.append(author_struct)
    return author_struct_array


def search_citation(source, document):
    """source(STRING) is the name of the database; document is a string just like 1-100_300-400"""
    if source == "ScienceDirectDataSource":
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()

    else:
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()
    doc_num = document.split('_')
    citation_struct_array = []
    for doc_num_iter in doc_num:
        doc_num_range = doc_num_iter.split('-')
        doc_num_start = doc_num_range[0]
        doc_num_end = doc_num_range[1]
        for i in range(int(doc_num_start), int(doc_num_end)+1):
            if (('_default', str(i)) in docset.keys()):
                doc = docset[('_default', str(i))]
                coredata = doc.metadatas['coredata']
                coredata_dict = coredata.meta_dict
                ref = doc.metadatas['references']
                ref_dict = ref.meta_dict
                citation_struct = {}
                citation_struct['doc_id'] = i
                if ('doi' in coredata_dict.keys()):
                    citation_struct['doc_doi'] = coredata_dict['doi']
                else:
                    citation_struct['doc_doi'] = 'none'
                if ('title' in coredata_dict.keys()):
                    citation_struct['title'] = coredata_dict['title']
                else:
                    citation_struct['title'] = 'none'
                citation_struct['bib_number'] = len(ref_dict['bibbliography-section']['references'])
                citation_struct['bib_detail'] = ref_dict['bibbliography-section']['references']
                citation_struct_array.append(citation_struct)
    return citation_struct_array


def search_text(source, document):
    """source(STRING) is the name of the database; document is a string just like 1-100_300-400"""
    if source == "ScienceDirectDataSource":
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()

    else:
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()
    doc_num = document.split('_')
    text_struct_array = []
    for doc_num_iter in doc_num:
        doc_num_range = doc_num_iter.split('-')
        doc_num_start = doc_num_range[0]
        doc_num_end = doc_num_range[1]
        for i in range(int(doc_num_start), int(doc_num_end)+1):
            if (('_default', str(i)) in docset.keys()):
                doc = docset[('_default', str(i))]
                coredata = doc.metadatas['coredata']
                coredata_dict = coredata.meta_dict
                text_struct = {}
                text_struct['doc_id'] = i
                if ('doi' in coredata_dict.keys()):
                    text_struct['doc_doi'] = coredata_dict['doi']
                else:
                    text_struct['doc_doi'] = 'none'
                if ('title' in coredata_dict.keys()):
                    text_struct['title'] = coredata_dict['title']
                else:
                    text_struct['title'] = 'none'
                text_struct['text'] = doc.get_text()
                text_struct_array.append(text_struct)
    return text_struct_array


def search_all(source, document):
    """source(STRING) is the name of the database; document is a string just like 1-100_300-400"""
    if source == "ScienceDirectDataSource":
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()

    else:
        ds = ScienceDirectDS(config)
        docset = ds.read_docset()
    doc_num = document.split('_')
    all_struct_array = []
    for doc_num_iter in doc_num:
        doc_num_range = doc_num_iter.split('-')
        doc_num_start = doc_num_range[0]
        doc_num_end = doc_num_range[1]
        for i in range(int(doc_num_start), int(doc_num_end) + 1):
            if (('_default', str(i)) in docset.keys()):
                doc = docset[('_default', str(i))]
                coredata = doc.metadatas['coredata']
                coredata_dict = coredata.meta_dict
                creator = coredata_dict['creator']
                ref = doc.metadatas['references']
                ref_dict = ref.meta_dict
                all_struct = {}
                all_struct['doc_id'] = i
                if ('doi' in coredata_dict.keys()):
                    all_struct['doc_doi'] = coredata_dict['doi']
                else:
                    all_struct['doc_doi'] = 'none'
                if ('title' in coredata_dict.keys()):
                    all_struct['title'] = coredata_dict['title']
                else:
                    all_struct['title'] = 'none'
                all_struct['author_number'] = 1
                all_struct['author_list'] = [creator]
                all_struct['bib_number'] = len(ref_dict['bibbliography-section']['references'])
                all_struct['bib_detail'] = ref_dict['bibbliography-section']['references']
                all_struct['text'] = doc.get_text()
                all_struct_array.append(all_struct)
    return all_struct_array

# if __name__ == '__main__':
    # print(search_all("ScienceDirectDataSource","1-10"))
