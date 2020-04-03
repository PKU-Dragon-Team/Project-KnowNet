# ieee_retrieval.py
import typing as tg
import math
import json
import time
import requests


class IEEERetrieval():
    # 根据检索词进行检索并解析元数据
    # 实现方式是模拟用户向ieeexplore发出检索请求，而不是调用API
    def __init__(
        self,
        query,
        paper_id_manager,
        offset=0,             # 偏移量。即从第几个开始获取
        num_result=-1,        # 获取多少元数据。-1表示所有的。
        request_interval=5    # 两次请求之间的时间间隔
    ) -> None:

        self.query = query
        self._paper_id_manager = paper_id_manager
        self._offset = offset
        self._num_result = num_result
        self._interval = request_interval

    def retrieve(self) -> None:
        '''发送检索请求，将请求响应（解析前的json文件）以dict格式
        记录在self.retrieve_results'''
        start_page = math.floor(self._offset / 100)     # 检索结果中每页有100篇文献
        if self._num_result == -1:
            end_page = 10000000000
        else:
            end_page = math.ceil((self._offset + self._num_result) / 100)

        self.retrieve_results = []

        post_url = "https://ieeexplore.ieee.org/rest/search/"
        data = {
            'queryText': self.query,
            'newsearch': 'true',
            'rowsPerPage': '100'
        }

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '98',
            'Content-Type': 'application/json',
            'Host': 'ieeexplore.ieee.org',
            'Origin': 'https://ieeexplore.ieee.org',
            'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=' + self.query,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        payload_data = {
            "queryText": self.query,
            "highlight": "true",
            "returnType": "SEARCH",
            "rowsPerPage": "100",
            "returnFacets": ["ALL"],
        }

        for i in range(start_page, end_page):
            print('crawling metadata page:', i, '/', end_page)
            try:
                payload_data['pageNumber'] = str(i+1)
                payload_data_json = json.dumps(payload_data)

                response = requests.post(post_url, json=data, headers=headers, data=payload_data_json)
                response.raise_for_status()

                records = response.json()['records']
                self.retrieve_results.extend(records)

            except Exception:
                break
            time.sleep(self._interval)
        print('finished crawling metadata pages.')
        print('and get metadata of %d papers' % len(self.retrieve_results))

    def parse(self) -> tg.Dict:
        '''将retrieve()获取的self.retrieve_results解析成Project-KnowNet系统格式'''
        self.parsed_results = []
        for result in self.retrieve_results:
            parsed_result = {}

            # 1. 将所有key之间有直接一一对应关系的解析出来
            keys_map = [    # (系统中字段名, 检索结果元数据中字段名)
                ('title', 'articleTitle'),
                ('abstract', 'abstract'),
                ('publication', 'publicationTitle'),
                ('year', 'publicationYear'),
                ('volume', 'volume'),
                ('issue', 'issue'),
                ('doi', 'doi'),
            ]

            for parsed_key, origin_key in keys_map:
                try:
                    parsed_result[parsed_key] = result[origin_key]
                    # ieeexplore会将结果中的检索词高亮显示，如[::keyword::]，因此要去除这些高亮标记。
                    # 高亮标记经常出现在title、abstract、publication中，但其它地方也许也会出现
                    # 因此对所有字符串字段都进行一次检查。
                    if isinstance(parsed_result[parsed_key], str):
                        parsed_result[parsed_key] = parsed_result[parsed_key].replace('[::', '').replace('::]', '')

                except Exception:
                    parsed_result[parsed_key] = None

            # 2. 解析文献类型type
            try:
                if result['isConference']:
                    parsed_result['type'] = 'conference'
                elif result['isBook']:
                    parsed_result['type'] = 'book'
                elif result['isJournalAndMagazine'] or result['isJournal'] or result['isMagazine']:
                    parsed_result['type'] = 'journal'
                elif result['isStandard']:
                    parsed_result['type'] = 'standard'
                else:
                    parsed_result['type'] = None
            except Exception:
                parsed_result['type'] = None

            # 3. 取作者中对应字段
            try:
                authors_origin = result['authors']
                parsed_result['authors'] = []
                author_keys_map = [
                    ('normalizedName', 'normalizedName'),
                    ('firstName', 'firstName'),
                    ('lastName', 'lastName'),
                ]

                for idx, author in enumerate(authors_origin):
                    parsed_author = {}
                    for parsed_key, origin_key in author_keys_map:
                        try:
                            parsed_author[parsed_key] = author[origin_key]
                        except Exception:
                            parsed_author[parsed_key] = None
                    parsed_author['order'] = idx + 1

                    parsed_result['authors'].append(parsed_author)
                parsed_result['authorCount'] = len(parsed_result['authors'])

            except Exception:
                parsed_result['authors'] = []

            # 4. 为本条记录分配一个id
            parsed_result['id'] = self._paper_id_manager.get_id(parsed_result['title'])
            self.parsed_results.append(parsed_result)

        # 只要解析并返回用户需要的从offset开始的前num_result个结果就好了。
        self.parsed_results = self.parsed_results[self._offset % 100:]
        if self._num_result > 0:
            self.parsed_results = self.parsed_results[: self._num_result]
        return self.parsed_results
