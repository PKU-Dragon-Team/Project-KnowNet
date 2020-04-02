# scopus_metadata_spider.py

from ..dependencies.elsapy.elsclient import ElsClient
from ..dependencies.elsapy.elssearch import ElsSearch
import json
import urllib.parse

import os
import collections
import typing as tg


class ScopusRetrieval():
    # 根据检索词query调用API进行检索，保存一些包括doi在内的简单的元数据。
    # 更全面的元数据可以通过ScopusMetadataSpider调用Elsevier摘要API获取。
    def __init__(self, 
                query, 
                num_result= -1,               # Get the first num_result results. -1 for all. No greater than 5000.  
                output_filename='retrieval_result.json',   # The file to store the Project-Knownet formatted metadata. 
                config= './data_fetcher/scopus/config.json'
                ) -> None:
        # output_filename: the file to store the metadata result. [query]_metadata.json for default. 
        
        con_file = open(config)
        config = json.load(con_file)
        con_file.close()
        
        # URL encode the query to fit the server's format requirements.
        self.query = urllib.parse.quote(query)
        self.query = self.query.replace('%2B', '%20')
    
        self.num_result = num_result
    
        self.output_filename = output_filename
        
        self._client = ElsClient(config['apikey'])
        self._client.inst_token = config['insttoken']
        
        # the spider pipeline: retrieve the query -> parse the result
        # self.retrieve()
        # self.parse()
    
    def retrieve(self) -> None:
        # Start a retrival using the given query. 
        # Returns the json-formatted result. 
        els_search = ElsSearch(self.query, index='scopus')
        els_search.execute(self._client, num_result=self.num_result)
        self._total_num_res = els_search.tot_num_res
        self.results = els_search.results       
        print('Number of results got with query', self.query, ':', len(self.results))

    def parse(self) -> None:
        # parse the results from ElsSearch to the json format we defined
        # and dump into a json file.
        output_json = []
        for i in range(len(self.results)):
            raw = self.results[i]
            parsed = self.parse_raw(raw)
            output_json.append(parsed)

        with open(self.output_filename, 'w', encoding='utf-8') as f:
            formatted_output_json = json.dumps(output_json, indent=4)
            f.write(formatted_output_json)
    
    
    def parse_raw(self, raw) -> None:
        # the specific format translate function
        # if a key of the dict doesn't exist, return None instead of raising an error. 
        raw_dd = collections.defaultdict(int)
        for k in raw:
            raw_dd[k] = raw[k]
        
        parsed = {
            'source': 'scopus',
            'spiderID': None,
            'id': None,
            'title': raw_dd['dc:title'],
            'abstract': None,
            'keywords': None,
            'type': None,
            'publication': raw_dd['prism:publicationName'],
            'volume': raw_dd['prism:volume'],
            'issue': raw_dd['prism:issue'],
            'doi': raw_dd['prism:doi'], 
            'uri': None,
            'authorCount': 0,
            'authors': []
        }
        
        # resolve publish year & month from prism:coverDate field
        try:
            parsed['year'] = raw_dd['prism:coverDate'].split('-')[0]
        except IndexError as e:
             parsed['year'] = None
        
        try:
            parsed['month'] = raw_dd['prism:coverDate'].split('-')[1]
        except IndexError as e:
             parsed['year'] = None

        try:
            if isinstance(raw_dd['authors']['author'], list) or isinstance(raw_dd['authors']['author'], dict):
                for idx, au in enumerate(raw_dd['authors']['author']):
                    if isinstance(au, dict):
                        au = au['$']
                    new_author = {
                        'id': None,
                        'order': idx + 1,
                        'isCorrespondingAuthor': None,
                        'normalizedName': au,
                    }
                    parsed['authors'].append(new_author)
                parsed['authorCount'] = len(parsed['authors'])
                
            else:
                new_author = {
                        'id': None,
                        'order': 1,
                        'correspondingAuthor': None,
                        'normalizedName': raw_dd['authors']['author'],
                    }
                parsed['authors'].append(new_author)
                parsed['authorCount'] = len(parsed['authors'])
                
        except Exception as e:
            pass
        
        return parsed
            
    def get_doi_list(self) -> tg.List:
        # 返回所有检索到的文档的doi，为接下来获取元数据做准备
        doi_list = []
        for res in self.results:
            doi = res['prism:doi']
            doi_list.append(doi)
        return doi_list