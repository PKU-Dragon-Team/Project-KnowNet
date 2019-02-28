import os
import sys
import tempfile
import unittest as ut
from pathlib import Path

from .base import BaseTestDataSource

root_folder = Path(os.getcwd())
sys.path.append(str(root_folder))

SAMPLE_DOC = {
    'pep':
    8,
    'authors': ['Guido van Rossum <guido at python.org>', 'Barry Warsaw <barry at python.org>', 'Nick Coghlan <ncoghlan at gmail.com>'],
    'status':
    'Active',
    'type':
    'Process',
    'created':
    '05-Jul-2001',
    'title':
    'PEP 8 -- Style Guide for Python Code',
    'sections':
    [{
        'title':
        'Introduction',
        'paragraphs': [
            '''This document gives coding conventions for the Python code comprising the standard library in the main Python distribution. '''
            '''Please see the companion informational PEP describing style guidelines for the C code in the C implementation of Python [1].''',
            '''his document and PEP 257 (Docstring Conventions) were adapted from Guido's original Python Style Guide essay, '''
            '''with some additions from Barry's style guide [2].''', '''This style guide evolves over time as additional conventions are identified and past '''
            '''conventions are rendered obsolete by changes in the language itself.''',
            '''Many projects have their own coding style guidelines. In the event of any conflicts, '''
            '''such project-specific guides take precedence for that project.'''
        ]
    },
     {
         'title':
         'A Foolish Consistency is the Hobgoblin of Little Minds',
         'paragraphs': [
             '''One of Guido's key insights is that code is read much more often than it is written. '''
             '''The guidelines provided here are intended to improve the readability of code and make it consistent '''
             '''across the wide spectrum of Python code. As PEP 20 says, "Readability counts".''',
             '''A style guide is about consistency. Consistency with this style guide is important. Consistency within a project is more important. '''
             '''Consistency within one module or function is the most important.''',
             '''However, know when to be inconsistent -- sometimes style guide recommendations just aren't applicable. '''
             '''When in doubt, use your best judgment. Look at other examples and decide what looks best. And don't hesitate to ask!''',
             '''In particular: do not break backwards compatibility just to comply with this PEP!''',
             '''Some other good reasons to ignore a particular guideline:''',
             '''1. When applying the guideline would make the code less readable, even for someone who is used to reading code that follows this PEP.''',
             '''2. To be consistent with surrounding code that also breaks it (maybe for historic reasons) -- '''
             '''although this is also an opportunity to clean up someone else's mess (in true XP style).''',
             '''3. Because the code in question predates the introduction of the guideline and there is no other reason to be modifying that code.''',
             '''4. When the code needs to remain compatible with older versions of Python that don't support the feature recommended by the style guide.'''
         ]
     }]
}

SAMPLE_DOC2 = {
    'title': 'PEP 484 -- Type Hints',
    'pep': 484,
    'authors': ['Guido van Rossum <guido at python.org>', 'Jukka Lehtosalo <jukka.lehtosalo at iki.fi>', 'Łukasz Langa <lukasz at python.org>'],
    'status': 'Provisional',
    'type': 'Standards Track',
    'created': '29-Sep-2014'
}


class TestDocDataSource(BaseTestDataSource):
    def test_default_create(self):
        from data_platform.datasource.abc.doc import DocKeyPair

        with tempfile.TemporaryDirectory(prefix='test_', suffix='_docds') as tmpdir:
            ds = self.get_test_instance(tmpdir)
            r_value = ds.create_doc(val=SAMPLE_DOC)
            del ds

            self.assertEqual(r_value, [DocKeyPair(docset_name='_default', doc_name='_default')])

    def test_default_read(self):
        with tempfile.TemporaryDirectory(prefix='test_', suffix='_docds') as tmpdir:
            ds = self.get_test_instance(tmpdir)
            doc_key = ds.create_doc(val=SAMPLE_DOC)
            r_value = ds.read_doc()
            del ds

            self.assertEqual(r_value, {doc_key[0]: SAMPLE_DOC})

    def test_named_create_and_read(self):
        from data_platform.datasource.abc.doc import DocKeyPair

        with tempfile.TemporaryDirectory(prefix='test_', suffix='_docds') as tmpdir:
            ds = self.get_test_instance(tmpdir)
            doc_key = ds.create_doc(key={('pep', 'pep484'): {}}, val=SAMPLE_DOC2)
            r_value = ds.read_doc()
            del ds

            self.assertEqual(doc_key, [DocKeyPair(docset_name='pep', doc_name='pep484')])
            self.assertEqual(r_value, {doc_key[0]: SAMPLE_DOC2})

    def test_multi_update(self):
        from data_platform.datasource.abc.doc import DocKeyPair

        with tempfile.TemporaryDirectory(prefix='test_', suffix='_docds') as tmpdir:
            ds = self.get_test_instance(tmpdir)
            doc_key = ds.update_doc([('pep', 'pep001'), ('pep', 'pep051'), ('pep', 'pep511')], SAMPLE_DOC2)
            del ds

            self.assertCountEqual(doc_key, [
                DocKeyPair(docset_name='pep', doc_name='pep511'),
                DocKeyPair(docset_name='pep', doc_name='pep051'),
                DocKeyPair(docset_name='pep', doc_name='pep001')
            ])

    def test_delete(self):
        from data_platform.datasource.abc.doc import DocKeyPair

        with tempfile.TemporaryDirectory(prefix='test_', suffix='_docds') as tmpdir:
            ds = self.get_test_instance(tmpdir)

            ds.create_doc(val=SAMPLE_DOC)
            ds.create_doc(key={('pep', 'pep484'): {}}, val=SAMPLE_DOC2)

            self.assertEqual(ds.delete_doc(key={('pep', 'pep484'): {}}), 1)
            docs = ds.read_doc()
            self.assertNotIn(DocKeyPair(docset_name='pep', doc_name='pep484'), docs)
            self.assertIn(DocKeyPair(docset_name='_default', doc_name='_default'), docs)

            ds.delete_doc()
            self.assertFalse(ds.read_doc())

            del ds

    def test_other_method(self):
        with tempfile.TemporaryDirectory(prefix='test_', suffix='_docds') as tmpdir:
            ds = self.get_test_instance(tmpdir)

            ds.flush()
            ds.clear()
            ds.reload()

            del ds


class TestJSONDS(TestDocDataSource):
    @classmethod
    def get_test_class(cls):
        from data_platform.datasource import JSONDS
        return JSONDS

    def get_test_instance(self, temp_location):
        from data_platform.config import ConfigManager
        from data_platform.datasource import JSONDS
        config = ConfigManager({"init": {"location": temp_location}})
        jsonds = JSONDS(config)
        return jsonds


@ut.skip('function-restricted implementation')
class TestScienceDirectDS(TestDocDataSource):
    @classmethod
    def get_test_class(cls):
        from data_platform.datasource import ScienceDirectDS

        return ScienceDirectDS

    def get_test_instance(self, temp_location):
        from data_platform.config import ConfigManager
        from data_platform.datasource import ScienceDirectDS

        config = ConfigManager({"init": {"location": temp_location}})
        ds = ScienceDirectDS(config)
        return ds


class TestMongoDBDS(TestDocDataSource):
    def setUp(self):
        """Optional initalizations."""
        ds = self.get_test_instance(None)
        ds.clear()

    @classmethod
    def get_test_class(cls):
        from data_platform.datasource.mongodb import MongoDBDS
        return MongoDBDS

    def get_test_instance(self, temp_location):
        from data_platform.config import ConfigManager, get_global_config
        from data_platform.datasource.mongodb import MongoDBDS

        global_conf = get_global_config()
        uri = global_conf.check_get(['test', 'mongodb', 'uri'])
        database = global_conf.check_get(['test', 'mongodb', 'database'])
        config = ConfigManager({"init": {"uri": uri, 'database': database}})
        mongodbds = MongoDBDS(config)
        return mongodbds

    def tearDown(self):
        """Optional finalizations."""
        ds = self.get_test_instance(None)
        ds.clear()
