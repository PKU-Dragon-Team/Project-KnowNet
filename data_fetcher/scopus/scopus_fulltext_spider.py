# scopus_fulltext_spider.py
import json
import logging
import typing as tg
import os

from ..dependencies.elsapy.elsdoc import FullDoc
from ..dependencies.elsapy.elsclient import ElsClient


class ScopusFulltextSpider:
    '''通过调用Elsevier的全文API检索指定doi的全文。
    全文结果将以xml格式储存在output_path目录下。'''
    def __init__(
            self, doi: str,
            filename=None,
            output_path='./data/Scopus/',
            config='./data_fetcher/scopus/config.json',
            log_file='./data/ieee_fulltext_spider_log.txt'
    ) -> None:

        # 初始化类
        con_file = open(config)
        config = json.load(con_file)
        con_file.close()

        self._client = ElsClient(config['apikey'])
        self._client.inst_token = config['insttoken']
        self.doi = doi
        self.doc = FullDoc(doi=doi)

        self.output_path = output_path
        if self.output_path[-1] not in ['/', '\\']:
            self.output_path += '/'

        self.filename = filename
        if self.filename is None:
            self.filename = doi.replace('/', '_').replace('\\', '_') + '.json'

        # 爬取失败时记录日志。
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.WARNING)
        format_str = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s: %(message)s')
        fh = logging.FileHandler(filename=log_file)
        fh.setFormatter(format_str)
        self._logger.addHandler(fh)

    def execute(self) -> tg.Optional[str]:
        '''根据doi执行对全文获取API的调用。
        如果获取成功，就将结果写入指定文件夹指定的文件名内，返回全文的文件路径
        如果获取失败，记录日志并返回None。
        '''
        succ = self.doc.read(els_client=self._client)
        if succ:
            # 成功找到原文，将检索结果保存至文件夹中
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
            with open(self.output_path + self.filename, 'w', encoding='utf-8') as f:
                f.write(str(self.doc.data))
            return self.output_path + self.filename
        err_msg = self.doc.err_msg
        self._logger.error('ScopusFulltextSpider, getting doi = %s failed. Exception: %s', self.doi, str(err_msg))
        return None
