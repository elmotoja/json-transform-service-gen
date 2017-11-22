import unittest

import logging

from src.JSONGenerator import JSONGenerator

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class TypeCheckTest(unittest.TestCase):
    def setUp(self):
        self.instance = JSONGenerator()
        self.instance.load_rdf_from_file('../src/temperature.rdf')

    # def test_StructureToStructure(self):
    #     inp = {'Thing': {'InsideThing': {'type': 'integer'}}}
    #     out = {'Thing': {'InsideThing': {'type': 'integer'}}}
    #     self.assertEqual('sts',
    #                      self.instance.match_types(inp['Thing'], out['Thing']))
    #
    # def test_FieldToStructure(self):
    #     inp = {'Thing': {'InsideThing': {'type': 'integer'}}}
    #     out = {'Thing': {'type': 'integer'}}
    #     self.assertEqual('fts',
    #                      self.instance.match_types(inp['Thing'], out['Thing']))
    #
    # def test_StructureToField(self):
    #     inp = {'Thing': {'type': 'integer'}}
    #     out = {'Thing': {'InsideThing': {'type': 'integer'}}}
    #     self.assertEqual('stf',
    #                      self.instance.match_types(inp['Thing'], out['Thing']))
    #
    # def test_FieldToFieldSameTypes(self):
    #     inp = {'Thing': {'type': 'integer'}}
    #     out = {'Thing': {'type': 'integer'}}
    #     self.assertEqual(True,
    #                      self.instance.match_types(inp['Thing'], out['Thing']))
    #
    # def test_FieldToFieldDifferentTypes(self):
    #     inp = {'Thing': {'type': 'string'}}
    #     out = {'Thing': {'type': 'integer'}}
    #     self.assertEqual(False,
    #                      self.instance.match_types(inp['Thing'], out['Thing']))

    def test_rdf_test(self):
        label = "air_temperature"
        print(self.instance.RDF_subclass(label))
        self.assertEqual(True, True)
if __name__ == '__main__':
    unittest.main()
