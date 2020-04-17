# scopus_metadata_spider.py
import json
import typing as tg
import logging

from ..dependencies.elsapy.elsclient import ElsClient
from ..dependencies.elsapy.elsdoc import AbsDoc
from data_platform.datasource.mongodb import MongoDBDS
from data_fetcher.id_manager import IDManager


class ScopusMetadataSpider:
    # 通过调用Elsevier的abstract API检索指定doi的元数据。
    def __init__(
        self,
        doi: tg.Text,
        paper_id_manager: IDManager,
        config='./data_fetcher/scopus/config.json',
        paper_set: tg.Text = None
    ) -> None:

        # 初始化这个类，传入要获取元数据的doi
        con_file = open(config)
        config = json.load(con_file)
        con_file.close()

        self._client = ElsClient(config['apikey'])
        self._client.inst_token = config['insttoken']

        self.doi = doi
        self.doc = AbsDoc(uri='https://api.elsevier.com/content/abstract/doi/' + doi)

        self._paper_id_manager = paper_id_manager
        self.paper_set = paper_set

        self.data: tg.Dict = {}
        self.parsed_data: tg.Dict = {}

    def execute(self) -> tg.Dict:
        # 调用接口获取API，并解析，返回符合Project-Knownet格式的解析结果
        self.data = self.read()
        self.parsed_data = self.parse()
        return self.parsed_data

    def read(self) -> tg.Optional[tg.Dict]:
        succ = self.doc.read(els_client=self._client)
        if succ:
            return self.doc.data
        return None

    def save(self, dbms: MongoDBDS):
        '''将解析后的元数据通过dbms存储在数据库中'''
        dbms.save_metadata(metadata=self.parsed_data, paper_set=self.paper_set)

    def save(self, dbms: MongoDBDS):
        '''将解析后的元数据通过dbms存储在数据库中'''
        dbms.save_metadata(metadata=self.parsed_data, paper_set=self.paper_set)

    def parse(self) -> tg.Dict:
        # 如果获取的是摘要，返回的json中（即self.data）有作者信息和引文信息。
        # 从结果中将这些内容解析出来，并作为返回值返回

        # 1. 解析标题
        try:
            title = self.data['abstracts-retrieval-response']['coredata']['dc:title']
        except (KeyError, TypeError, IndexError):
            title = None

        # 2. 解析出版物相关信息
        try:
            publication = self.data['abstracts-retrieval-response']['coredata']['prism:publicationName']
        except (KeyError, TypeError, IndexError):
            publication = None

        try:
            pub_volume = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['volisspag']['voliss']['@volume']
        except (KeyError, TypeError, IndexError):
            pub_volume = None

        try:
            pub_issue = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['volisspag']['voliss']['@issue']
        except (KeyError, TypeError, IndexError):
            pub_issue = None

        # 3. 解析出版时间
        try:
            pub_year = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['publicationdate']['year']
        except (KeyError, TypeError, IndexError):
            pub_year = None

        try:
            pub_month = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['publicationdate']['month']
        except (KeyError, TypeError, IndexError):
            pub_month = None

        # 4. 解析作者。
        try:
            author_raw = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['author-group']
        except (KeyError, TypeError, IndexError):
            author_raw = []
        # author_raw的数据结构：若干个元素，每个元素对应一个机构和从属这个机构的作者们

        authors = []
        # 先根据通讯作者信息记录通讯作者的normalized name，然后在authors列表中找到这个人，
        try:
            corresAuthorNormalizedName = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['correspondence']['person']['ce:indexed-name']
        except (KeyError, TypeError, IndexError):
            corresAuthorNormalizedName = None

        # 遍历每个机构，机构中的每位作者，解析其信息并作为对象添加到authors列表中
        try:
            for affili in author_raw:
                try:
                    nationality = affili['affiliation']['country']
                except (KeyError, TypeError, IndexError):
                    nationality = None

                try:
                    address = affili['affiliation']['ce:source-text']
                except (KeyError, TypeError, IndexError):
                    address = None

                try:
                    if isinstance(affili['affiliation']['organization'], list):
                        organization = affili['affiliation']['organization'][0]['$']
                    else:
                        organization = affili['affiliation']['organization']['$']
                except (KeyError, TypeError, IndexError):
                    organization = None

                try:
                    for au in affili['author']:
                        # au的数据结构：若干个元素，每个元素对应一位作者
                        author = {}
                        try:
                            author['order'] = au['@seq']
                        except (KeyError, TypeError, IndexError):
                            author['order'] = None

                        try:
                            author['normalizedName'] = au['preferred-name']['ce:indexed-name']
                        except (KeyError, TypeError, IndexError):
                            author['normalizedName'] = None

                        if author['normalizedName'] == corresAuthorNormalizedName:
                            author['isCorrespondingAuthor'] = 'true'
                        else:
                            author['isCorrespondingAuthor'] = 'false'

                        try:
                            author['firstName'] = au['preferred-name']['ce:given-name']
                        except (KeyError, TypeError, IndexError):
                            author['firstName'] = None

                        try:
                            author['lastName'] = au['preferred-name']['ce:surname']
                        except (KeyError, TypeError, IndexError):
                            author['lastName'] = None

                        author['address'] = address
                        author['nationality'] = nationality
                        author['organization'] = organization
                        author['orcid'] = None
                        author['middleName'] = None
                        authors.append(author)
                except (KeyError, TypeError, IndexError):
                    pass
        except (KeyError, TypeError, IndexError):
            pass

        # 对authors列表根据其作者位次进行排序
        authors.sort(key=lambda x: int(x['order']))

        # 通过不同的normalizedName和order统计作者数量。考虑到共同一作或重名的情况，只要name和order有一个不同就算两位不同的作者。
        try:
            au_list = [au['normalizedName'] + au['order'] for au in authors]
            au_set = list(set(au_list))
            author_count = len(au_set)
        except (KeyError, TypeError, IndexError):
            author_count = None

        # 5. 解析摘要内容
        try:
            abstract = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['abstracts']
        except (KeyError, TypeError, IndexError):
            abstract = None

        # 6. 解析参考文献数量和每条的内容
        try:
            reference_raw = self.data['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']
        except (KeyError, TypeError, IndexError):
            reference_raw = None

        references = []
        try:
            referencesCount = reference_raw['@refcount']
        except (KeyError, TypeError, IndexError):
            referencesCount = None

        try:
            for ref in reference_raw['reference']:
                reference = {}
                try:
                    reference['order'] = ref['@id']
                except (KeyError, TypeError, IndexError):
                    reference['order'] = None

                try:
                    reference['title'] = ref['ref-info']['ref-title']['ref-titletext']
                except (KeyError, TypeError, IndexError):
                    reference['title'] = None

                # 为解析到的每篇文章分配一个id
                try:
                    reference['id'] = self._paper_id_manager.get_id(reference['title'])
                except (KeyError, TypeError, IndexError):
                    reference['id'] = None

                try:
                    reference['publication'] = ref['ref-info']['ref-sourcetitle']
                except (KeyError, TypeError, IndexError):
                    reference['publication'] = None

                try:
                    reference['year'] = ref['ref-info']['ref-publicationyear']['@first']
                except (KeyError, TypeError, IndexError):
                    reference['year'] = None

                try:
                    reference['volume'] = ref['ref-info']['ref-volisspag']['voliss']['@volume']
                except (KeyError, TypeError, IndexError):
                    reference['volume'] = None

                none_keys = ('month', 'issue', 'type')
                for none_key in none_keys:
                    reference[none_key] = None

                try:
                    ref_authors_raw = ref['ref-info']['ref-authors']['author']
                except (KeyError, TypeError, IndexError):
                    ref_authors_raw = None

                ref_authors = []
                try:
                    for au in ref_authors_raw:
                        ref_author = {}
                        try:
                            ref_author['order'] = au['@seq']
                        except (KeyError, TypeError, IndexError):
                            ref_author['order'] = None

                        try:
                            ref_author['normalizedName'] = au['ce:indexed-name']
                        except (KeyError, TypeError, IndexError):
                            ref_author['normalizedName'] = None

                        try:
                            ref_author['lastName'] = au['ce:surname']
                        except (KeyError, TypeError, IndexError):
                            ref_author['lastName'] = None

                        none_keys_author = ('isCorrespondingAuthor', 'firstName', 'middleName', 'orcid', 'address', 'nationality', 'organization')
                        for none_key in none_keys_author:
                            ref_author[none_key] = None

                        ref_authors.append(ref_author)
                except (KeyError, TypeError, IndexError):
                    pass

                reference['authors'] = ref_authors
                reference['authorCount'] = len(ref_authors)
                references.append(reference)
        except (KeyError, TypeError, IndexError):
            pass

        # 7. 解析文献类型。
        try:
            source_type = self.data['abstracts-retrieval-response']['coredata']['prism:aggregationType']
        except (KeyError, TypeError, IndexError):
            source_type = None

        # 8. 解析关键词
        try:
            keyword_raw = self.data['abstracts-retrieval-response']['authkeywords']['author-keyword']
            keywords = []
            for kw in keyword_raw:
                keywords.append(kw['$'])
        except (KeyError, TypeError, IndexError):
            keywords = []

        # 9. 为本文分配一个id
        id_ = self._paper_id_manager.get_id(title)

        # 最后返回一个dict，表示解析出的结果
        return {
            'source': 'Scopus',
            'id': id_,
            'title': title,
            'abstract': abstract,
            'keywords': keywords,
            'type': source_type,
            'publication': publication,
            'year': pub_year,
            'month': pub_month,
            'volume': pub_volume,
            'issue': pub_issue,
            'doi': self.doi,
            'uri': None,    # 在获取全文前先将uri设为None
            'authorCount': author_count,
            'authors': authors,
            'referencesCount': referencesCount,
            'references': references,
            'content': None     # 在解析全文前先将content设为None
        }
