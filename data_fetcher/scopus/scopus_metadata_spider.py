# scopus_fulltext_spider.py

from elsapy.elsclient import ElsClient
from elsapy.elssearch import ElsSearch
from elsapy.elsdoc import FullDoc, AbsDoc

import collections
import json

class ScopusMetadataSpider(object):
    # 通过调用Elsevier的abstract API检索指定doi的元数据。
    def __init__(self, 
                 doi,
                 config='config.json'):
        
        # 初始化这个类，传入要获取元数据的doi
        con_file = open(config)
        config = json.load(con_file)
        con_file.close()
        
        self._client = ElsClient(config['apikey'])
        self._client.inst_token = config['insttoken']
        
        self.doi = doi
        self.doc = AbsDoc(uri = 'https://api.elsevier.com/content/abstract/doi/' + doi)
    
    def execute(self):
        # 调用接口获取API，并解析，返回符合Project-Knownet格式的解析结果
        self.data = self.read()
        return self.parse()
    
    def read(self):
        succ = self.doc.read(els_client = self._client)
        if succ:
            return self.doc._data
        else:
            return None
    
    def parse(self):
        # 如果获取的是摘要，返回的json中（即self.data）有作者信息和引文信息。
        # 从结果中将这些内容解析出来，并作为返回值返回
        
        # 1. 解析标题
        try:
            title = self.data['abstracts-retrieval-response']['coredata']['dc:title']
        except Exception as e:
            title = None
        
        # 2. 解析出版物相关信息
        try:
            publication = self.data['abstracts-retrieval-response']['coredata']['prism:publicationName']
        except Exception as e:
            publication = None
            
        try:
            pub_volume = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['volisspag']['voliss']['@volume']
        except Exception as e:
            pub_volume = None
        
        try:
            pub_issue = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['volisspag']['voliss']['@issue']
        except Exception as e:
            pub_issue = None

        # 3. 解析出版时间
        try:
            pub_year = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['publicationdate']['year']
        except Exception as e:
            pub_year = None
        
        try:
            pub_month = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['publicationdate']['month']
        except Exception as e:
            pub_month = None
             
        # 4. 解析作者。
        try:
            author_raw = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['author-group']
        except Exception as e:
            author_raw = None
            
        # author_raw的数据结构：若干个元素，每个元素对应一个机构和从属这个机构的作者们
        
        authors = []
        # 先根据通讯作者信息记录通讯作者的normalized name，然后在authors列表中找到这个人，
        try:
            corresAuthorNormalizedName = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['correspondence']['person']['ce:indexed-name']
        except Exception as e:
            corresAuthorNormalizedName = None
            
        # 遍历每个机构，机构中的每位作者，解析其信息并作为对象添加到authors列表中
        for affili in author_raw:
            try:
                nationality             = affili['affiliation']['country']
            except Exception as e:
                nationality             = None

            try:
                address                 = affili['affiliation']['ce:source-text']
            except Exception as e:
                address                 = None
    
            try:
                if isinstance(affili['affiliation']['organization'], list):
                    organization        = affili['affiliation']['organization'][0]['$']
                else:
                    organization        = affili['affiliation']['organization']['$']
            except Exception as e:
                organization            = None
                
            try:  
                for au in affili['author']:
                    # au的数据结构：若干个元素，每个元素对应一位作者
                    author = {}
                    try:
                        author['order']             = au['@seq']
                    except Exception as e:
                        author['order']             = None
                        
                    try:
                        author['normalizedName']    = au['preferred-name']['ce:indexed-name']
                    except Exception as e:
                        author['normalizedName']    = None
                            
                    if author['normalizedName'] == corresAuthorNormalizedName:
                        author['isCorrespondingAuthor'] = 'true'
                    else: 
                        author['isCorrespondingAuthor'] = 'false'
                
                    try:                 
                        author['firstName']         = au['preferred-name']['ce:given-name']
                    except Exception as e:
                        author['firstName']         = None
                    
                    try:
                        author['lastName']          = au['preferred-name']['ce:surname']
                    except Exception as e:
                        author['lastName']          = None
                        
                    author['address']           = address
                    author['nationality']       = nationality
                    author['organization']      = organization
                    authors.append(author)
            except Exception as e:
                pass
        # 对authors列表根据其作者位次进行排序
        authors.sort(key=lambda x: int(x['order']))
        
        # 通过不同的normalizedName和order统计作者数量。考虑到共同一作或重名的情况，只要name和order有一个不同就算两位不同的作者。
        try:
            au_list =  [au['normalizedName'] + au['order'] for au in authors]
            au_set = list(set(au_list))
            author_count = len(au_set)
        except Exception as e:
            author_count = None
            
         
        # 5. 解析摘要内容
        try:
            abstract = self.data['abstracts-retrieval-response']['item']['bibrecord']['head']['abstracts']
        except Exception as e:
            abstract = None
                
        # 6. 解析参考文献数量和每条的内容
        try:
            reference_raw = self.data['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']
        except Exception as e:
            reference_raw = None
    
        references = []
        try:
            referencesCount = reference_raw['@refcount']
        except Exception as e:
            referencesCount = None
            
        try:
            for ref in reference_raw['reference']:
                reference = {}
                try:
                    reference['order']          = ref['@id']
                except Exception as e:
                    reference['order']          = None
                
                try:
                    reference['title']          = ref['ref-info']['ref-title']['ref-titletext']
                except Exception as e:
                    reference['title']          = None
                    
                try:
                    reference['publication']    = ref['ref-info']['ref-sourcetitle']
                except Exception as e:
                    reference['publication']    = None
                
                try:
                    reference['year']           = ref['ref-info']['ref-publicationyear']['@first']
                except Exception as e:
                    reference['year']           = None

                try:
                    reference['volume']         = ref['ref-info']['ref-volisspag']['voliss']['@volume']
                except Exception as e:
                    reference['volume']         = None
                    
                try: 
                    ref_authors_raw = ref['ref-info']['ref-authors']['author']
                except Exception as e:
                    ref_authors_raw = None
                    
                ref_authors = []
                try:
                    for au in ref_authors_raw:
                        ref_author = {}
                        try:
                            ref_author['order']             = au['@seq']
                        except Exception as e:
                            ref_author['order']             = None
                            
                        try:
                            ref_author['normalizedName']    = au['ce:indexed-name']
                        except Exception as e:
                            ref_author['normalizedName']    = None
    
                        try:
                            ref_author['lastName']          = au['ce:surname']
                        except Exception as e:
                            ref_author['lastName']          = None
                            
                        ref_authors.append(ref_author)
                except Exception as e:
                    pass
                
                reference['authors'] = ref_authors
                reference['authorCount'] = len(ref_authors)
                references.append(reference)
        except Exception as e:
            pass
                    
        # 7. 解析文献类型。
        try:
            source_type = self.data['abstracts-retrieval-response']['coredata']['prism:aggregationType']
        except Exception as e:
            source_type = None
            
        # 8. 解析关键词
        try:
            keyword_raw = self.data['abstracts-retrieval-response']['authkeywords']['author-keyword']
            keywords = []
            for kw in keyword_raw:
                keywords.append(kw['$'])
        except Exception as e:
            keywords = []

        # 最后返回一个dict，表示解析出的结果
        return {
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
            'authorCount': author_count,
            'authors': authors,
            'referencesCount': referencesCount,
            'references': references,     
        }

if __name__ == "__main__":
    sfs = ScopusMetadataSpider(doi = '10.1016/j.antiviral.2020.104742')
    parsed = sfs.execute()
    parsed = json.dumps(parsed, indent=4, sort_keys=False)
    with open('abs_parsed.json', 'w', encoding='utf-8') as f:
        f.write(parsed)