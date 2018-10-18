"""Packages for data source classes
"""

import os
import sys
import typing as tg
from abc import ABC, abstractmethod
from pathlib import Path
from collections import defaultdict

from lxml import etree

from . import document as _doc

from traceback import format_exception


class BaseDataSource(ABC):
    """abstract base class for all data sources
    """

    def __init__(self, source: tg.Any, *args, **kwargs) -> None:
        self._source = source
        self._init_args = args
        self._init_kwargs = kwargs

    @property
    def source(self) -> tg.Any:
        """get the current data source
        """
        return self._source

    @abstractmethod
    def items(self, limit: int = -1) -> _doc.DocumentSet:
        """return a DocumentSet that contains first n items in data source
        if limit < 0 then return all items
        if 0 <= limit < len(datasource) then return n items
        if limit >= len(datasource) then return all items
        """
        pass

    @abstractmethod
    def __getitem__(self, key: tg.Any) \
            -> tg.Union[_doc.Document, _doc.DocumentSet]:
        """return the item(s) that meets the key
        if key is not in the data source, a KeyError will be raised
        if don't want the Error, use get method instead
        """
        pass

    @abstractmethod
    def get(self, key: tg.Any, default: tg.Any = None) \
            -> tg.Union[_doc.Document, _doc.DocumentSet]:
        """return the item(s) that meets the key
        if key is not in the data source, default will be returned
        """
        pass


class OrientDBDataSource(BaseDataSource):
    pass


class XMLDataSource(BaseDataSource):
    pass


class ScienceDirectDataSource(BaseDataSource):
    """data source class for reading ScienceDirect XML response
    """

    def __init__(self, source: tg.Union[tg.Text, Path], *args, **kwargs) \
            -> None:
        super().__init__(source, *args, **kwargs)

        path = Path(source)

        self._file_list = self._path_check(path)

        self._path = path
        self._mtime = 0.0

    @staticmethod
    def _path_check(path: Path) -> tg.List[Path]:
        if not path.exists():
            raise ValueError("The source path is not exist: " f"{str(path)}")

        if path.is_file():
            file_list = [path]
        elif path.is_dir():
            file_list = sorted(path.rglob("*.xml"))
        else:
            raise ValueError(
                "The source path is neither a file nor a directory: "
                f"{str(path)}")

        return file_list

    @staticmethod
    def _find_with_ns(node: etree.Element,
                      query: tg.Text) -> tg.Optional[etree.Element]:
        return node.find(query, node.nsmap)

    def _load(self) -> None:
        mtime = os.path.getmtime(self._path)

        if mtime != self._mtime:
            # the directory is new, reload
            self._mtime = mtime
            self._file_list = self._path_check(self._path)
            self._parsed_doclist: tg.List[_doc.Document] = []
            for i, xmlfile in enumerate(self._file_list):
                try:
                    parsed = self._parse_one(xmlfile, i)
                    self._parsed_doclist.append(parsed)
                # except ValueError:
                #     pass
                except Exception as e:
                    print(
                        f"Parsing file {str(xmlfile)} error: ",
                        e,
                        file=sys.stderr)
                    for line in format_exception(None, e, e.__traceback__):
                        print(line, file=sys.stderr)

    @staticmethod
    def _tag_without_ns(tag: tg.Text) -> tg.Text:
        if '}' in tag:
            end = tag.find('}')
            return tag[end + 1:]
        else:
            return tag

    def _parse_body(
            self, body: etree.Element, doc_id: int
    ) -> tg.Tuple[tg.List[_doc.Section], tg.Dict[tg.Text, tg.List[tg.Text]]]:

        bibid2paraid: tg.Dict[tg.Text, tg.List[tg.Text]] = defaultdict(list)

        sections = self._find_with_ns(body, 'ce:sections')
        nsmap = sections.nsmap
        sec_list: tg.List[_doc.Section] = []
        for sec in sections.iterfind('ce:section', nsmap):
            sec_attr = {**sec.attrib}
            sec_attr['doc_id'] = doc_id

            # section-title
            sec_title = sec.find('ce:section-title', nsmap)
            title_para = _doc.Paragraph([_doc.Text(sec_title.text.strip())],
                                        **sec_title.attrib)
            # paragraph
            para_list: tg.List[_doc.Paragraph] = [title_para]
            sec_elem = _doc.Section(
                [], section_title=sec_title.text, **sec_attr)
            for para_id, para in enumerate(sec.iterfind('ce:para', nsmap)):
                para_attr = {**para.attrib}
                para_attr['doc_id'] = doc_id
                para_attr['parent'] = sec_elem
                if 'id' not in para_attr:
                    para_attr['id'] = f'para{para_id}'

                inline_list: tg.List[_doc.Inline] = []
                inline_list.append(_doc.Text(para.text.strip()))
                para_elem = _doc.Paragraph([], **para_attr)

                for child in para:
                    raw_tag = self._tag_without_ns(child.tag)

                    attrib = {**child.attrib}
                    attrib['doc_id'] = doc_id
                    attrib['parent'] = para_elem

                    # crossref
                    if raw_tag.startswith('cross-ref'):
                        sup = child.find('ce:sup', nsmap)
                        if sup is None:
                            text = '[' + child.text.strip(
                            ) if child.text else "" + ']'
                        else:
                            text = '[' + sup.text.strip() + ']'

                        if raw_tag.endswith('s'):
                            attrib['refid'] = attrib['refid'].split()
                        else:
                            attrib['refid'] = [attrib['refid']]

                        for bibid in attrib['refid']:
                            bibid2paraid[bibid].append(para_attr['id'])
                    else:
                        # other
                        text = child.text.strip() if child.text else ""

                    tag = _doc.Tag(raw_tag, text, attrib)
                    inline_list.append(tag)

                    if child.tail:
                        inline_list.append(
                            _doc.Text(child.tail.rstrip(), parent=para_elem))

                para_elem.set_content(inline_list)
                para_list.append(para_elem)
            sec_elem.set_content(para_list)
            sec_list.append(sec_elem)
        return sec_list, bibid2paraid

    def _parse_tail(self, tail: etree.Element, doc_id: int) -> _doc.MetaData:
        bib = self._find_with_ns(tail, 'ce:bibliography')

        if bib is None:
            raise ValueError('Source file has no bibliography')

        attr = {**bib.attrib}

        # section-title
        title = self._find_with_ns(bib, 'ce:section-title')

        title_attr = {**title.attrib}
        title_attr['text'] = title.text.rstrip()

        attr['section-title'] = title_attr

        # bib-sec
        bib_sec = self._find_with_ns(bib, 'ce:bibliography-sec')
        bibsec_attr = {**bib_sec.attrib}

        nsmap = bib_sec.nsmap
        refs: tg.Dict[str, tg.Dict] = {}
        for bib_ref in bib_sec.iterfind('ce:bib-reference', nsmap):
            ref_dict = {**bib_ref.attrib}

            label = self._find_with_ns(bib_ref, 'ce:label')
            ref_dict['label'] = label.text.strip()

            ref = self._find_with_ns(bib_ref, 'sb:reference')
            if ref is not None:
                contrib = self._find_with_ns(
                    ref, 'sb:contribution')  # author and title

                if contrib is not None:
                    ref_dict['authors'] = []
                    authors = self._find_with_ns(contrib, 'sb:authors')
                    if authors is not None:
                        for author in authors.iterfind('sb:author', nsmap):
                            author_dict: tg.Dict[str, str] = {}
                            for child in author:
                                author_dict[self._tag_without_ns(
                                    child.tag)] = child.text.strip()
                            ref_dict['authors'].append(author_dict)

                    ref_title = self._find_with_ns(contrib, 'sb:title')
                    if ref_title is not None:
                        title_dict: tg.Dict[str, str] = {}
                        for child in ref_title:
                            title_dict[self._tag_without_ns(
                                child.tag)] = child.text.strip()
                        ref_dict['title'] = title_dict

                host = self._find_with_ns(ref, 'sb:host')  # series and pages
                if host is not None:
                    for host_child in host:
                        tag = self._tag_without_ns(host_child.tag)
                        if tag.endswith('issue'):
                            issue = host_child

                            series = self._find_with_ns(issue, 'sb:series')

                            for series_child in series:
                                raw_tag = self._tag_without_ns(
                                    series_child.tag)
                                if raw_tag.endswith('title'):
                                    issue_title_dict: tg.Dict[str, str] = {}
                                    for child in series_child:
                                        issue_title_dict[self._tag_without_ns(
                                            child.tag)] = child.text.strip()
                                    ref_dict['host_title'] = issue_title_dict
                                else:
                                    ref_dict[self._tag_without_ns(
                                        series_child.tag
                                    )] = series_child.text.strip()

                            date = self._find_with_ns(issue, 'sb:date')
                            ref_dict['date'] = date.text.strip()
                        elif tag.endswith('pages'):
                            pages = host_child
                            pages_dict: tg.Dict[tg.Text, tg.Text] = {}
                            for page_child in pages:
                                pages_dict[self._tag_without_ns(
                                    page_child.tag)] = page_child.text.strip()
                            ref_dict['pages'] = pages_dict
                        else:
                            ref_dict[self._tag_without_ns(
                                host_child.tag)] = host_child.text.strip()

            other_ref = self._find_with_ns(bib_ref, 'ce:other-ref')
            if other_ref is not None:
                textref = self._find_with_ns(other_ref, 'ce:textref')
                ref_dict['textref'] = textref.text.strip()

            refs[ref_dict['id']] = ref_dict

        bibsec_attr['references'] = refs
        attr['bibbliography-section'] = bibsec_attr

        return _doc.MetaData("bibliography", attr)

    def _parse_one(self, xmlfile: Path, index: int) -> _doc.Document:
        tree = etree.parse(str(xmlfile))
        root = tree.getroot()

        doc_meta = {}

        # coredata
        coredata = self._find_with_ns(root, 'coredata')

        if coredata is None:
            raise ValueError('Source file has no coredata')

        coredata_attr = {}
        for child in coredata:
            text = child.text
            coredata_attr[self._tag_without_ns(
                child.tag)] = text.strip() if text else ""
        coremeta = _doc.MetaData('coredata', coredata_attr)
        doc_meta['coredata'] = coremeta

        # originalText
        ot = self._find_with_ns(root, 'originalText')

        if ot is None:
            raise ValueError('Source file has no originalText')

        articles: tg.List[etree.Element] = ot.xpath(
            '//*[local-name() = $name]', name='article')

        if not articles:
            raise ValueError('Source file has no article')

        article = articles[0]

        # body
        body = self._find_with_ns(article, 'body')

        if body is None:
            raise ValueError('Source file has no body')

        sec_list, bib2para = self._parse_body(body, index)
        doc_root = _doc.Root(sec_list)

        bibid2paraid = _doc.MetaData('bibid_to_paraid', bib2para)
        doc_meta['bib2para'] = bibid2paraid

        # tail
        tail = self._find_with_ns(article, 'tail')

        if tail is None:
            raise ValueError('Source file has no tail')

        references = self._parse_tail(tail, index)
        doc_meta['references'] = references

        return _doc.Document(doc_root, doc_meta)

    def __del__(self) -> None:
        """Close the file and do other cleaning
        """
        pass

    def items(self, limit: int = -1) -> _doc.DocumentSet:
        self._load()
        return _doc.DocumentSet(self._parsed_doclist)

    def __getitem__(
            self,
            key: tg.Any
            ) -> tg.Union[_doc.Document, _doc.DocumentSet]:  # yapf: disable
        raise NotImplementedError(
            'This method is not supported now, use items()')

    def get(
            self,
            key: tg.Any,
            default: tg.Any = None
            ) -> tg.Union[_doc.Document, _doc.DocumentSet]:  # yapf: disable
        raise NotImplementedError(
            'This method is not supported now, use items()')
