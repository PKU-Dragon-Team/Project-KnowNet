"""Package for document classes
"""

import typing as tg
from abc import ABC, abstractmethod
from collections.abc import Iterable
from itertools import chain


class DocumentSet(Iterable):
    """Class represents a set of documents
    """

    def __init__(self, doc_list: tg.Iterable['Document']) -> None:
        self.docs = list(doc_list)

    def __iter__(self):
        return iter(self.docs)

    def __len__(self):
        return len(self.docs)

    def __getitem__(self, key):
        return self.docs[key]

    def add_document(self, doc: 'Document') -> None:
        self.docs.append(doc)


class Document:
    """Class represents one document
    """

    def __init__(self, root: 'Root',
                 metadata: tg.Dict[tg.Text, 'MetaData']) -> None:
        self.root = root
        self.metadata = metadata

    def __iter__(self) -> tg.Iterator['Section']:
        return iter(self.root)

    def __getitem__(self, key) -> 'Section':
        return self.root[key]

    # get method

    def get_text(self) -> tg.Text:
        return self.root.get_text()

    def get_sections(self) -> tg.List['Section']:
        return self.root.get_sections()

    def get_metadata(self) -> tg.Dict[tg.Text, 'MetaData']:
        return self.metadata

    def get_paragraphs(self) -> tg.Dict[tg.Text, 'Paragraph']:
        paras = (chain.from_iterable(
            sec.get_paragraphs() for sec in self.root.sections))
        return {para.get_id(): para for para in paras}

    # section manipulate

    def add_section(self, section: 'Section') -> None:
        self.root.add_section(section)

    def clear_sections(self) -> None:
        self.root.clear_sections()


class Element(ABC):
    """Abstract base class for any in-document elements
    """

    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs

    @abstractmethod
    def get_text(self) -> tg.Text:
        pass

    def get_id(self) -> tg.Text:
        return str(id(self))

    def get_documentid(self) -> tg.Text:
        if 'doc_id' not in self._init_kwargs:
            raise AttributeError('The element has no associate document')
        else:
            return self._init_kwargs['doc_id']

    def get_parent(self) -> 'Element':
        if 'parent' not in self._init_kwargs:
            raise AttributeError('The element has no associate parent')
        else:
            return self._init_kwargs['parent']


class Root(Element):
    """Class represents the root element of a document
    """

    def __init__(
            self,
            section_list: tg.List['Section'],
            *args, **kwargs) -> None:  # yapf: disable
        super().__init__(*args, **kwargs)
        self.sections = section_list

    def __iter__(self) -> tg.Iterator['Section']:
        return iter(self.sections)

    def __getitem__(self, key) -> 'Section':
        return self.sections[key]

    def get_text(self) -> tg.Text:
        return ''.join(sec.get_text() for sec in self.sections)

    def get_sections(self) -> tg.List['Section']:
        subsec_list = list(
            chain.from_iterable(
                sec.get_subsections() for sec in self.sections))
        if subsec_list:
            return subsec_list
        else:
            return self.sections

    def get_parentid(self) -> tg.Text:
        return self.get_documentid()

    def add_section(self, section: 'Section') -> None:
        self.sections.append(section)

    def clear_sections(self) -> None:
        self.sections.clear()


class MetaData(Element):
    """Class represents a metadata element of a document
    """

    def __init__(
            self,
            meta_name: tg.Text,
            meta_dict: tg.Dict[tg.Text, tg.Any],
            *args, **kwargs) -> None:  # yapf: disable
        super().__init__(*args, **kwargs)
        self.meta_name = meta_name
        self.meta_dict = meta_dict

    def get_text(self) -> tg.Text:
        return ""


class Box(Element):
    """Class represents a box element with a sequence of contents
    """
    def __init__(
            self,
            content_list: tg.Iterable['Element'],
            *args, **kwargs) -> None:  # yapf: disable

        super().__init__(*args, **kwargs)
        self.content_list = list(content_list)

    def __getitem__(self, key):
        return self.content_list[key]

    def get_text(self) -> tg.Text:
        return '\n'.join(c.get_text() for c in self.content_list) + '\n'

    def set_content(self, content_list: tg.Iterable['Element']) -> None:
        self.content_list = list(content_list)


class Section(Box):
    """Class represents a section element of a document
    a section can contain multiple sections OR paragraphs, but not both
    """
    def __init__(
            self,
            content_list: tg.Iterable['Box'],
            *args, **kwargs) -> None:  # yapf: disable

        super().__init__(content_list, *args, **kwargs)

    def get_subsections(self) -> tg.List['Section']:
        sec_list = [
            box for box in self.content_list if isinstance(box, Section)
        ]
        if sec_list:
            return list(
                chain.from_iterable(box.get_subsections()
                                    for box in self.content_list
                                    if isinstance(box, Section)))
        else:
            return []

    def get_paragraphs(self) -> tg.List['Paragraph']:
        para_list = [
            box for box in self.content_list if isinstance(box, Paragraph)
        ]
        if para_list:
            return para_list
        else:
            return list(
                chain.from_iterable(box.get_paragraphs()
                                    for box in self.content_list
                                    if isinstance(box, Section)))


class Paragraph(Box):
    """Class represents a paragraph element of a document
    """
    def __init__(
            self,
            content_list: tg.Iterable['Inline'],
            *args, **kwargs) -> None:  # yapf: disable
        super().__init__(content_list, *args, **kwargs)

    def get_text(self) -> tg.Text:
        return ''.join(c.get_text() for c in self.content_list)

    def get_id(self) -> tg.Text:
        try:
            return self._init_kwargs['id']
        except KeyError:
            return super().get_id()


class Inline(Element):
    """Abstract Base class for any in-line element
    """
    pass


class Text(Inline):
    """Class for in-line text
    """

    def __init__(self, content: tg.Text, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.content = content

    def get_text(self) -> tg.Text:
        return self.content if self.content else ""


class Tag(Inline):
    """Class for in-line tag
    """
    def __init__(
            self,
            tag_name: tg.Text,
            tag_text: tg.Text,
            tag_attr: tg.Dict[tg.Text, tg.Text],
            *args, **kwargs) -> None:  # yapf: disable

        super().__init__(*args, **kwargs)
        self.tag_name = tag_name
        self.tag_text = tag_text
        self.tag_attr = tag_attr

    def get_text(self) -> tg.Text:
        return self.tag_text if self.tag_text else ""
