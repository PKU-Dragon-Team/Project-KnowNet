# ieee_fulltext_spider.py
import requests
import time
import re
import logging


class IEEEFulltextSpider(object):
    # 根据IEEE的article_number获取pdf。
    # 实现方式是构造url，并模拟用户向ieeexplore发送请求，而不是调用API。
    def __init__(
        self, article_number,
        filename=None,
        output_path='./data/IEEE_PDF/',
        log_file='./data/ieee_fulltext_spider_log.txt',
        request_interval=10      # 两次请求之间的时间间隔，建议在10s以上
    ) -> None:
        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'ieeexplore.ieee.org',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36}'
        }

        self._base_url = 'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='
        self.article_number = str(article_number)
        self._url = self._base_url + str(self.article_number)
        self._interval = request_interval

        self.output_path = output_path
        if self.output_path[-1] not in ['/', '\\']:
            self.output_path += '/'

        self.filename = filename
        if self.filename is None:
            self.filename = self.article_number + '.pdf'

        # 爬取失败时记录日志。
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        format_str = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s: %(message)s')
        fh = logging.FileHandler(filename=log_file)
        fh.setFormatter(format_str)
        self._logger.addHandler(fh)

    def execute(self) -> bool:
        '''爬取PDF。第一个post是为了获取重定位到的pdf的url，第二个get是为了访问这个url。
        NOTE: 发送get请求前先sleep，是为了防止爬的速度太快。
        全文内容反爬限制很严格，强烈建议两个请求之间间隔至少10秒！
        没使用多线程也是为了防止爬得太快，绝对不是因为我懒。
        '''
        time.sleep(self._interval)

        self._response = requests.post(self._url, headers=self._headers)
        try:
            pdf_url = re.findall(r'https://.+\.pdf', self._response.text)[0]
        except Exception as e:
            self._logger.error(
                'IEEEFulltextSpider, articleNumber = ' + self.article_number + ' PDF URL not found. Exception: ' + str(e)
            )
            return False

        try:
            u = requests.get(pdf_url)
            with open(self.output_path + self.filename, 'wb') as f:
                f.write(u.content)
        except Exception as e:
            self._logger.error(
                'IEEEFulltextSpider, articleNumber = ' + self.article_number + ' error when downloading PDF. Exception: ' + str(e)
            )
            return False

        return self.output_path + self.filename
