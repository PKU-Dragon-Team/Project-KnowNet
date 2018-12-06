"""Data source class for reading ScienceDirect XML response."""

import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Text, Tuple

from defusedxml.lxml import parse as etree_parse
from lxml import etree

from .. import document as _doc
from ..config import ConfigManager
from ..document import Document, Element
from .abc.doc import DocDataSource, DocFactory, DocKeyPair, DocKeyType, DocValDict
from .exception import NotSupportedError


class ScienceDirectFactory(DocFactory):
    @classmethod
    def pack(cls, doc_dict: DocValDict) -> Document:
        # root
        root = doc_dict["root"]
        root_node = _doc.Root.from_dict(root)

        # metadata
        meta_out = {}
        metadatas = doc_dict["metadata"]
        for metadata in metadatas:
            meta_name = metadata["meta_name"]
            meta = metadata["meta"]
            meta_out[meta_name] = _doc.MetaData.from_dict(meta)

        return Document(root_node, meta_out)

    @classmethod
    def unpack(cls, doc: Document) -> DocValDict:
        result: Dict[Text, Any] = {}

        root_object = doc.root
        result['root'] = root_object.to_dict()

        metadatas = doc.metadatas
        result['metadata'] = [{
            "meta_name": meta_name,
            "meta": metadata.to_dict(),
        } for meta_name, metadata in metadatas.items()]

        return result


class ScienceDirectDS(DocDataSource):
    """Data source class for reading ScienceDirect XML response."""

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        path = Path(config.check_get(["init", "location"]))

        self._path = path
        self._mtime = 0.0
        self._factory: Optional[DocFactory] = ScienceDirectFactory()
        self._data: Dict[Text, Dict] = {}

        self._load()

    @staticmethod
    def _xml_files(path: Path) -> List[Path]:
        if not path.exists():
            raise ValueError(f"The source path is not exist: {str(path)}")

        if path.is_dir():
            return list(path.rglob("*.xml"))

        return []

    @staticmethod
    def _find_with_ns(node: etree.ElementBase, query: Text) -> List[etree.ElementBase]:
        result = node.find(query, node.nsmap)
        if result is None:
            return []
        if isinstance(result, etree.ElementBase):
            return [result]
        return list(result)

    @classmethod
    def _find_one_with_ns(cls, node: etree.ElementBase, query: Text) -> etree.ElementBase:
        result = cls._find_with_ns(node, query)
        if not result:
            raise ValueError(f'There is no {query}.')
        return result[0]

    @staticmethod
    def _xpath(node: etree.ElementBase, query: Text, *args, **kwargs) -> List[etree.ElementBase]:
        result = node.xpath(query, *args, **kwargs)
        if result is None:
            return []
        if isinstance(result, etree.ElementBase):
            return [result]
        return result

    @staticmethod
    def _xpath_one(node: etree.ElementBase, query: Text, *args, **kwargs) -> etree.ElementBase:
        result = node.xpath(query, *args, **kwargs)
        if not result:
            raise ValueError(f'Query {query} has no result.')
        return result[0]

    def _load(self) -> None:
        mtime = os.path.getmtime(self._path)

        if mtime != self._mtime:
            # the directory is new, reload
            self._mtime = mtime
            for xmlfile in self._xml_files(self._path):
                try:
                    parsed = self._parse_one(xmlfile)
                    self._data[xmlfile.stem] = ScienceDirectFactory.unpack(parsed)
                except ValueError as e:
                    print(f"Parsing file {str(xmlfile.name)} error: ", e, file=sys.stderr)

    @staticmethod
    def _tag_without_ns(tag: Text) -> Text:
        if '}' in tag:
            end = tag.find('}')
            return tag[end + 1:]
        return tag

    def _parse_body(self, body: etree.ElementBase) -> Tuple[List[_doc.Section], Dict[Text, List[Element]]]:
        bibid2para: Dict[Text, List[Element]] = defaultdict(list)
        sections = self._find_one_with_ns(body, 'ce:sections')
        nsmap = sections.nsmap
        sec_list: List[_doc.Section] = []
        for sec in sections.iterfind('ce:section', nsmap):
            # section-title
            sec_title = sec.find('ce:section-title', nsmap)
            title_para = _doc.Paragraph([_doc.Text(sec_title.text.strip())], **sec_title.attrib)
            # paragraph
            para_list: List[_doc.Paragraph] = [title_para]
            sec_elem = _doc.Section([], section_title=sec_title.text, **sec.attrib)
            for para in sec.iterfind('ce:para', nsmap):
                inline_list: List[_doc.Inline] = []
                inline_list.append(_doc.Text(para.text.strip()))
                para_elem = _doc.Paragraph([], **para.attrib)

                for child in para:
                    raw_tag = self._tag_without_ns(child.tag)

                    attrib = {**child.attrib}

                    # crossref
                    if raw_tag.startswith('cross-ref'):
                        sup = child.find('ce:sup', nsmap)
                        if sup is None:
                            text = '[' + child.text.strip() if child.text else "" + ']'
                        else:
                            text = '[' + sup.text.strip() + ']'

                        if raw_tag.endswith('s'):
                            attrib['refid'] = attrib['refid'].split()
                        else:
                            attrib['refid'] = [attrib['refid']]

                        for bibid in attrib['refid']:
                            bibid2para[bibid].append(para_elem)
                    else:
                        # other
                        text = child.text.strip() if child.text else ""

                    tag = _doc.Tag(raw_tag, text, attrib)
                    inline_list.append(tag)

                    if child.tail:
                        inline_list.append(_doc.Text(child.tail.rstrip()))

                para_elem.set_content(inline_list)
                para_list.append(para_elem)
            sec_elem.set_content(para_list)
            sec_list.append(sec_elem)
        return sec_list, bibid2para

    def _parse_tail(self, tail: etree.ElementBase) -> _doc.MetaData:
        bib = self._find_one_with_ns(tail, 'ce:bibliography')
        attr = {**bib.attrib}

        # section-title
        title = self._find_one_with_ns(bib, 'ce:section-title')
        title_attr = {**title.attrib}
        title_attr['text'] = title.text.rstrip()
        attr['section-title'] = title_attr

        # bib-sec
        bib_sec = self._find_one_with_ns(bib, 'ce:bibliography-sec')
        bibsec_attr = {**bib_sec.attrib}
        nsmap = bib_sec.nsmap
        refs: Dict[str, Dict] = {}
        for bib_ref in bib_sec.iterfind('ce:bib-reference', nsmap):
            ref_dict = {**bib_ref.attrib}
            label = self._find_one_with_ns(bib_ref, 'ce:label')
            ref_dict['label'] = label.text.strip()
            refs_ = self._find_with_ns(bib_ref, 'sb:reference')

            if refs_:
                # author and title
                contribs = self._find_with_ns(refs_[0], 'sb:contribution')
                if contribs:
                    contrib = contribs[0]
                    ref_dict['authors'] = []
                    authors = self._find_with_ns(contrib, 'sb:authors')
                    if authors:
                        for author in authors[0].iterfind('sb:author', nsmap):
                            author_dict: Dict[str, str] = {}
                            for child in author:
                                author_dict[self._tag_without_ns(child.tag)] = child.text.strip()
                            ref_dict['authors'].append(author_dict)

                    ref_titles = self._find_with_ns(contrib, 'sb:title')
                    if ref_titles:
                        title_dict: Dict[str, str] = {}
                        for child in ref_titles[0]:
                            title_dict[self._tag_without_ns(child.tag)] = child.text.strip()
                        ref_dict['title'] = title_dict

                    # series and pages
                host = self._find_one_with_ns(refs_[0], 'sb:host')
                for host_child in host:
                    tag = self._tag_without_ns(host_child.tag)
                    if tag.endswith('issue'):
                        issue = host_child

                        series = self._find_with_ns(issue, 'sb:series')
                        for series_child in series:
                            raw_tag = self._tag_without_ns(series_child.tag)
                            if raw_tag.endswith('title'):
                                issue_title_dict: Dict[str, str] = {}
                                for child in series_child:
                                    issue_title_dict[self._tag_without_ns(child.tag)] = child.text.strip()
                                ref_dict['host_title'] = issue_title_dict
                            else:
                                ref_dict[self._tag_without_ns(series_child.tag)] = series_child.text.strip()

                        date = self._find_one_with_ns(issue, 'sb:date')
                        ref_dict['date'] = date.text.strip()
                    elif tag.endswith('pages'):
                        pages = host_child
                        pages_dict: Dict[Text, Text] = {}
                        for page_child in pages:
                            pages_dict[self._tag_without_ns(page_child.tag)] = page_child.text.strip()
                        ref_dict['pages'] = pages_dict
                    else:
                        ref_dict[self._tag_without_ns(host_child.tag)] = host_child.text.strip()

            other_ref = self._find_with_ns(bib_ref, 'ce:other-ref')
            if other_ref:
                textref = self._find_one_with_ns(other_ref[0], 'ce:textref')
                ref_dict['textref'] = textref.text.strip()

            refs[ref_dict['id']] = ref_dict

        bibsec_attr['references'] = refs
        attr['bibbliography-section'] = bibsec_attr

        return _doc.MetaData(attr)

    def _parse_one(self, xmlfile: Path) -> Document:
        tree = etree_parse(str(xmlfile))
        root = tree.getroot()

        doc_meta = {}

        # coredata
        coredata = self._find_one_with_ns(root, 'coredata')
        coredata_attr = {}
        for child in coredata:
            text = child.text
            coredata_attr[self._tag_without_ns(child.tag)] = text.strip() if text else ""
        coremeta = _doc.MetaData(coredata_attr)
        doc_meta['coredata'] = coremeta

        # originalText
        ot = self._find_one_with_ns(root, 'originalText')
        articles = self._xpath(ot, '//*[local-name() = $name]', name='article')
        if not articles:
            raise ValueError('There is no article.')
        article = articles[0]

        # body
        body = self._find_one_with_ns(article, 'body')
        sec_list, bib2elem = self._parse_body(body)
        doc_root = _doc.Root(sec_list)

        # root created, id setted
        bib2para = {}
        for bibid, elems in bib2elem.items():  # type: Text, List[Element]
            bib2para[bibid] = [elem.id_ for elem in elems]
        bibid2para = _doc.MetaData(bib2para)
        doc_meta['bib2para'] = bibid2para

        # tail
        tail = self._find_one_with_ns(article, 'tail')
        references = self._parse_tail(tail)
        doc_meta['references'] = references

        return Document(doc_root, doc_meta)

    def create_doc(self, key: DocKeyType, val: DocValDict) -> NoReturn:
        raise NotSupportedError("ScienceDirectDS is read-only.")

    def read_doc(self, key: DocKeyType = DocKeyPair('@*', '@*')) -> Dict[DocKeyPair, DocValDict]:
        self._load()

        ds_d_c: List[Tuple] = self._format_doc_key(key)

        doc_names = set()
        for docset_name, doc_name, _ in ds_d_c:
            if docset_name not in ('@*', '_default'):
                print("Warning: ScienceDirectDS doesn't support multi-documentsets, all but '_default' will be converted to '@*'.", file=sys.stderr)

            if doc_name.startswith('@*'):
                for d_name in self._data:
                    # TODO: doc wildcards and filters
                    doc_names.add(d_name)
            else:
                doc_names.add(doc_name)

        result = {DocKeyPair('_default', doc_name): self._data[doc_name] for doc_name in doc_names}
        return result

    def update_doc(self, key: DocKeyType, val: DocValDict) -> NoReturn:
        raise NotSupportedError("ScienceDirectDS is read-only.")

    def delete_doc(self, key: DocKeyType) -> NoReturn:
        raise NotSupportedError("ScienceDirectDS is read-only.")

    def query(self, query: Text, *args, **kwargs) -> NoReturn:
        raise NotSupportedError("ScienceDirectDS has no query method.")
