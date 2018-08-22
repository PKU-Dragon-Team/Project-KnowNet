"""Package for document classes
"""

import typing as tg
from abc import ABC, abstractmethod
from collections import UserDict
from itertools import chain


class DocumentSet(UserDict):
    """Class represents a set of documents."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for doc_id, doc in self.data.items():
            doc.id_ = doc_id


class Document:
    """Class represents one document."""

    def __init__(self, root: 'Root', metadata_dict: tg.Dict[tg.Text, 'MetaData']) -> None:
        self._root = root
        self._metadata = metadata_dict

        self._id: tg.Text = ''

    def __iter__(self) -> tg.Iterator['Section']:
        return iter(self._root)

    def __getitem__(self, key) -> 'Section':
        return self._root[key]

    @property
    def id_(self) -> tg.Text:
        return self._id

    @id_.setter
    def id_(self, value) -> None:
        self._id = value
        self._root.document_id = value
        for meta in self._metadata.values():
            meta.document_id = value

    @property
    def root(self) -> 'Root':
        return self._root

    @property
    def metadatas(self) -> tg.Dict[tg.Text, tg.Any]:
        return self._metadata

    # get method

    def get_text(self) -> tg.Text:
        return self._root.get_text()

    def get_sections(self) -> tg.List['Section']:
        return self._root.get_sections()

    def get_paragraphs(self) -> tg.Dict[tg.Text, 'Paragraph']:
        paras: tg.Iterator[Paragraph] = (chain.from_iterable(sec.get_paragraphs() for sec in self._root.get_sections()))
        return {para.id_: para for para in paras}

    # section manipulate

    def add_section(self, section: 'Section') -> None:
        self._root.add_section(section)

    def clear_sections(self) -> None:
        self._root.clear_sections()


class Element(ABC):
    """Abstract base class for any in-document elements."""

    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs

        self._id: tg.Text = ''
        self._doc_id: tg.Text = ''

    # abstract method
    # # serialize/deserialize
    @classmethod
    @abstractmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'Element':
        pass

    @abstractmethod
    def to_dict(self) -> tg.Dict:
        pass

    # # hidden
    @abstractmethod
    def _post_set_id(self) -> None:
        pass

    @abstractmethod
    def _set_document_id(self) -> None:
        pass

    # # output
    @abstractmethod
    def get_text(self) -> tg.Text:
        pass

    # property
    @property
    def id_(self) -> tg.Text:
        """The id of current Element.
        Remain consistent in current Document object.
        """
        return self._id

    @id_.setter
    def id_(self, value: tg.Text):
        self._id = value
        self._post_set_id()

    @property
    def document_id(self) -> tg.Text:
        """The id of the Document of current Element.
        Remain consistent in current Document object.
        """
        return self._doc_id

    @document_id.setter
    def document_id(self, value: tg.Text) -> None:
        self._doc_id = value
        self._set_document_id()


class Root(Element):
    """Class represents the root element of a document."""

    def __init__(self, section_list: tg.List['Section'], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.sections = section_list
        self.id_ = '/root'

    def __iter__(self) -> tg.Iterator['Section']:
        return iter(self.sections)

    def __getitem__(self, key) -> 'Section':
        return self.sections[key]

    @classmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'Root':
        section_list = init_dict['section_list']
        init_args = init_dict.get('init_args', [])
        init_kwargs = init_dict.get('init_kwargs', {})

        seclist = [Section.from_dict(sec_dict) for sec_dict in section_list]
        return cls(seclist, *init_args, **init_kwargs)

    def to_dict(self) -> tg.Dict:
        section_list = [sec.to_dict() for sec in self.sections]
        init_args = self._init_args
        init_kwargs = self._init_kwargs
        return {'section_list': section_list, 'init_args': init_args, 'init_kwargs': init_kwargs}

    def _post_set_id(self) -> None:
        for idx, sec in enumerate(self.sections):
            sec.id_ = f'{self.id_}/sec_{idx}'

    def _set_document_id(self) -> None:
        for sec in self.sections:
            sec.document_id = self.document_id

    def get_text(self) -> tg.Text:
        return ''.join(sec.get_text() for sec in self.sections)

    def get_sections(self) -> tg.List['Section']:
        subsec_list = list(chain.from_iterable(sec.get_subsections() for sec in self.sections))
        if subsec_list:
            return subsec_list
        else:
            return self.sections

    def add_section(self, section: 'Section') -> None:
        self.sections.append(section)

    def clear_sections(self) -> None:
        self.sections.clear()


class MetaData(Element):
    """Class represents a metadata element of a document."""

    def __init__(self, meta_dict: tg.Dict[tg.Text, tg.Any], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.meta_dict = meta_dict
        self.id_ = '/metadata'

    @classmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'MetaData':
        meta_dict = init_dict['meta_dict']
        init_args = init_dict.get('init_args', [])
        init_kwargs = init_dict.get('init_kwargs', {})

        return cls(meta_dict, *init_args, **init_kwargs)

    def to_dict(self) -> tg.Dict:
        meta_dict = self.meta_dict
        init_args = self._init_args
        init_kwargs = self._init_kwargs
        return {'meta_dict': meta_dict, 'init_args': init_args, 'init_kwargs': init_kwargs}

    def _post_set_id(self) -> None:
        return

    def _set_document_id(self) -> None:
        return

    def get_text(self) -> tg.Text:
        return ""

    def __getitem__(self, key) -> tg.Dict[tg.Text, tg.Any]:
        return self.meta_dict[key]

    def __iter__(self) -> tg.Iterator[tg.Text]:
        return iter(self.meta_dict)

    def keys(self):
        return self.meta_dict.keys()

    def values(self):
        return self.meta_dict.values()

    def items(self):
        return self.meta_dict.items()


class Box(Element):
    """Abstract class represents a box element with a sequence of contents."""

    def __init__(self, content_list: tg.Iterable['Element'], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.content_list = list(content_list)

    def __getitem__(self, key) -> 'Element':
        return self.content_list[key]

    def __iter__(self) -> tg.Iterator['Element']:
        return iter(self.content_list)

    def get_text(self) -> tg.Text:
        return '\n'.join(c.get_text() for c in self.content_list) + '\n'

    def set_content(self, content_list: tg.Iterable['Element']) -> None:
        self.content_list = list(content_list)


class Section(Box):
    """Class represents a section element of a document.

    a section can contain multiple sections OR paragraphs, but not both
    """

    def __init__(self, content_list: tg.Iterable['Box'], *args, **kwargs) -> None:
        super().__init__(content_list, *args, **kwargs)

    @classmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'Section':
        subsections = init_dict.get('subsections')
        paragraphs = init_dict.get('paragraphs')
        init_args = init_dict.get('init_args', [])
        init_kwargs = init_dict.get('init_kwargs', {})

        contlist: tg.List['Box']
        if subsections:
            contlist = [Section.from_dict(sec_dict) for sec_dict in subsections]
        elif paragraphs:
            contlist = [Paragraph.from_dict(para_dict) for para_dict in paragraphs]
        else:
            contlist = []

        return cls(contlist, *init_args, **init_kwargs)

    def to_dict(self) -> tg.Dict:
        subsections = [sec.to_dict() for sec in self.content_list if isinstance(sec, Section)]
        paragraphs = [para.to_dict() for para in self.content_list if isinstance(para, Paragraph)]
        init_args = self._init_args
        init_kwargs = self._init_kwargs
        return {'subsections': subsections, 'paragraphs': paragraphs, 'init_args': init_args, 'init_kwargs': init_kwargs}

    def _post_set_id(self) -> None:
        for idx, content in enumerate(self.content_list):
            if isinstance(content, Section):
                content.id_ = f'{self.id_}/sec_{idx}'
            elif isinstance(content, Paragraph):
                content.id_ = f'{self.id_}/para_{idx}'
            else:
                content.id_ = f'{self.id_}/other_{idx}'

    def _set_document_id(self) -> None:
        for content in self.content_list:
            content.document_id = self.document_id

    def get_subsections(self) -> tg.List['Section']:
        sec_list = [box for box in self.content_list if isinstance(box, Section)]
        if sec_list:
            return list(chain.from_iterable(box.get_subsections() for box in self.content_list if isinstance(box, Section)))
        else:
            return []

    def get_paragraphs(self) -> tg.List['Paragraph']:
        para_list = [box for box in self.content_list if isinstance(box, Paragraph)]
        if para_list:
            return para_list
        else:
            return list(chain.from_iterable(box.get_paragraphs() for box in self.content_list if isinstance(box, Section)))


class Paragraph(Box):
    """Class represents a paragraph element of a document."""

    def __init__(self, content_list: tg.Iterable['Inline'], *args, **kwargs) -> None:
        super().__init__(content_list, *args, **kwargs)

    @classmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'Paragraph':
        inline_list = init_dict['inline_list']
        init_args = init_dict.get('init_args', [])
        init_kwargs = init_dict.get('init_kwargs', {})

        inline_list = [Tag.from_dict(idict) if idict["type"] == "tag" else Text.from_dict(idict) for idict in inline_list]
        return cls(inline_list, *init_args, **init_kwargs)

    def to_dict(self) -> tg.Dict:
        inline_list = [inline.to_dict() for inline in self.content_list]
        init_args = self._init_args
        init_kwargs = self._init_kwargs
        return {'inline_list': inline_list, 'init_args': init_args, 'init_kwargs': init_kwargs}

    def _post_set_id(self) -> None:
        for idx, inline in enumerate(self.content_list):
            inline.id_ = f'{self.id_}/inline_{idx}'

    def _set_document_id(self) -> None:
        for inline in self.content_list:
            inline.document_id = self.document_id

    def get_text(self) -> tg.Text:
        return ''.join(c.get_text() for c in self.content_list)


class Inline(Element):
    """Abstract Base class for any in-line element."""
    pass


class Text(Inline):
    """Class for in-line text."""

    def __init__(self, content: tg.Text, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.content = content

    @classmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'Text':
        type_ = init_dict['type']
        init_args = init_dict.get('init_args', [])
        init_kwargs = init_dict.get('init_kwargs', {})

        if type_ == 'text':
            content = init_dict['content']
        else:
            content = ''

        return cls(content, *init_args, **init_kwargs)

    def to_dict(self) -> tg.Dict:
        content = self.content
        init_args = self._init_args
        init_kwargs = self._init_kwargs
        return {'type': 'text', 'content': content, 'init_args': init_args, 'init_kwargs': init_kwargs}

    def _post_set_id(self) -> None:
        return

    def _set_document_id(self) -> None:
        return

    def get_text(self) -> tg.Text:
        return self.content if self.content else ""


class Tag(Inline):
    """Class for in-line tag."""

    def __init__(self, tag_name: tg.Text, tag_text: tg.Text, tag_attr: tg.Dict[tg.Text, tg.Text], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tag_name = tag_name
        self.tag_text = tag_text
        self.tag_attr = tag_attr

    @classmethod
    def from_dict(cls, init_dict: tg.Dict) -> 'Tag':
        type_ = init_dict['type']
        init_args = init_dict.get('init_args', [])
        init_kwargs = init_dict.get('init_kwargs', {})

        if type_ == 'tag':
            tag_name = init_dict['tag_name']
            tag_text = init_dict['tag_text']
            tag_attr = init_dict['tag_attr']
        else:
            raise ValueError('Wrong type for initialize Tag')

        return cls(tag_name, tag_text, tag_attr, *init_args, **init_kwargs)

    def to_dict(self) -> tg.Dict:
        tag_name = self.tag_name
        tag_text = self.tag_text
        tag_attr = self.tag_attr
        init_args = self._init_args
        init_kwargs = self._init_kwargs

        return {'type': 'tag', 'tag_name': tag_name, 'tag_text': tag_text, 'tag_attr': tag_attr, 'init_args': init_args, 'init_kwargs': init_kwargs}

    def _post_set_id(self) -> None:
        return

    def _set_document_id(self) -> None:
        return

    def get_text(self) -> tg.Text:
        return self.tag_text if self.tag_text else ""
