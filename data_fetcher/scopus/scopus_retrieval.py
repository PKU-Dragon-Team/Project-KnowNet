# scopus_metadata_spider.py

import json
import urllib.parse
import collections
import typing as tg
import logging

from ..dependencies.elsapy.elssearch import ElsSearch
from ..dependencies.elsapy.elsclient import ElsClient


class ScopusRetrieval():
    # 根据检索词query调用API进行检索，保存一些包括doi在内的简单的元数据。
    # 更全面的元数据可以通过ScopusMetadataSpider调用Elsevier摘要API获取。
    def __init__(
        self,
        query,
        num_result=-1,      # Get the first num_result results. -1 for all. No greater than 5000.
        config='./data_fetcher/scopus/config.json'
    ) -> None:
        # output_filename: the file to store the metadata result. [query]_metadata.json for default.

        con_file = open(config)
        config = json.load(con_file)
        con_file.close()

        # URL encode the query to fit the server's format requirements.
        self.query = urllib.parse.quote(query)
        self.query = self.query.replace('%2B', '%20')

        self.num_result = num_result

        self._client = ElsClient(config['apikey'])
        self._client.inst_token = config['insttoken']

        self._total_num_res = None
        self._results = None
        self._doi_list: tg.List[str] = []
        # the spider pipeline: retrieve the query -> parse the result
        # self.retrieve()
        # self.parse()

    def retrieve(self) -> None:
        # Start a retrival using the given query.
        # Record the json-formatted result in self.results.
        els_search = ElsSearch(self.query, index='scopus')
        els_search.execute(self._client, num_result=self.num_result)
        self._total_num_res = els_search.tot_num_res
        self._results = els_search.results
        logging.info('Number of results got with query %s: %d' % (self.query, len(self._results)))

    def get_doi_list(self) -> tg.List:
        # 返回所有检索到的文档的doi，为接下来获取元数据做准备
        self._doi_list = []
        for res in self._results:
            if self.num_result >= 0 and len(self._doi_list) >= self.num_result:
                break
            doi = res['prism:doi']
            self._doi_list.append(doi)
        return self._doi_list
