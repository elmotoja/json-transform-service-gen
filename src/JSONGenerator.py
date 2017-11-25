import json
import logging
from timeit import default_timer as timer
import sys

import rdflib
from jinja2 import Environment, FileSystemLoader

from synonymdict import SynonymDict
from utils.rdfprocessor import RDFProcessor
import transforms as transforms
from process_dict import process_dict

from nested_lookup import nested_lookup
from dictquery import DictQuery as dq

# https://github.com/russellballestrini/nested-lookup
# from utils import find_path
# import transforms
# from synonymdict import SynonymDict

# def ObjectFromSchemaFactory(schema):
#     builder = pjs.ObjectBuilder(schema)
#     clasessRepository = builder.build_classes()
#     return clasessRepository

logger = logging.getLogger('Generator')
logger.setLevel(logging.DEBUG)


# import PyDictionary


# import python_jsonschema_objects as pjs
# TODO: Nested dicts support
# TODO: RDF processor

class JSONGenerator:
    def __init__(self):
        self._template = None
        self._INPUT_SCHEMA = {}
        self._OUTPUT_SCHEMA = {}
        self._PROCESSED_INPUT = None
        self._PROCESSED_OUTPUT = None
        self._USER_DICT = None  # SynonymDict()
        self._USER_RDF = None
        logger.debug('{} created!'.format(self.__class__.__name__))

    def set_template_path(self, file_path='../templates/python_service.py'):
        template_folder_path = '/'.join(file_path.split('/')[:-1])
        template_file = file_path.split('/')[-1]
        env = Environment(loader=FileSystemLoader(template_folder_path))
        logger.debug(f'Template loaded from path: {file_path}')
        self._template = env.get_template(template_file)

    def add_dictionary(self, file_path):
        self._USER_DICT = SynonymDict()
        self._USER_DICT.load_from_file(file_path)

    # def load_rdf_from_file(self, file_path, format='n3'):
    #     self._USER_RDF = rdflib.Graph()
    #     self._USER_RDF.parse(file_path, format=format)
    #     logger.debug(f'RDF loaded from path: {file_path}')
    def load_rdf_from_file(self, file_path, format='n3'):
        self._USER_RDF = RDFProcessor()
        self._USER_RDF.load_rdf_from_file(file_path, format=format)
        # logger.debug(f'RDF loaded from path: {file_path}')

    def load_rdf_from_url(self):
        raise NotImplementedError('Function not implemented yet!')

    def load_schemas_from_file(self, input_schem, output_schem):
        with open(input_schem, 'r') as inFile, \
                open(output_schem, 'r') as outFile:
            self._INPUT_SCHEMA = json.loads(inFile.read())
            self._PROCESSED_INPUT = self._process_dict(self._INPUT_SCHEMA['properties'])
            self._OUTPUT_SCHEMA = json.loads(outFile.read())
            self._PROCESSED_OUTPUT = self._process_dict(self._OUTPUT_SCHEMA['properties'])

    def load_schemas_from_url(self):
        raise NotImplementedError('Function not implemented yet!')

    def transform(self, target_structure, given_structure):
        matches = []
        for field in target_structure.keys():
            if nested_lookup(field, given_structure):
                logger.debug(f'Property \'{field}\' found.')
                matches.append(self._match_types({field: target_structure[field]},
                                                 {field: nested_lookup(field, given_structure)[0]}))
                continue
            else:
                logger.debug(f'Property \'{field}\' not found.')
                if self._USER_DICT:
                    replacements = self._USER_DICT.replacements(field)[field]
                    logger.debug(f'Known replacements: {str(replacements)}')
                    for replacement in replacements:
                        if nested_lookup(replacement, given_structure):
                            logger.debug(f'Matching replacement found: {replacement}')
                            matches.append(self._match_types({field: target_structure[field]},
                                                             {replacement: nested_lookup(replacement, given_structure)[0]}))
                            continue
            if self._USER_RDF:
                synonyms = self._USER_RDF.synonyms(field)
                logger.debug(f'Known synonyms: {str(synonyms)}')
                for synonym in synonyms:
                    if nested_lookup(synonym, given_structure):
                        logger.debug(f'Matching synonym found: {synonym}')
                        matches.append(self._match_types({field: target_structure[field]},
                                                         {synonym: nested_lookup(synonym, given_structure)[0]}))
                        continue
                subclasses = self._USER_RDF.subclasses(field)
                logger.debug(f'Known subclasses: {str(subclasses)}')
                for subclass in subclasses:
                    if nested_lookup(subclass, given_structure):
                        logger.debug(f'Matching subclass found: {subclass}')
                        matches.append(self._match_types({field: target_structure[field]},
                                                         {subclass: nested_lookup(subclass, given_structure)[0]}))
                        continue
        return filter(None, matches)

    # def match_transformation(self, field):
    #     from jsonschema import validate
    #     if field in self.INPUT_SCHEMA['properties'].keys():
    #         logger.debug('{0} matched to {0}'. format(field))
    #         return self.match_types(field, field)
    #     else:
    #         logger.debug('Property \'{}\' not found. Known synonyms: {}'.format(field,
    #                                                                             str(self.USER_DICT.synonyms(field)[field])))
    #         for synon in self.USER_DICT.synonyms(field)[field]:
    #             if synon in self.INPUT_SCHEMA['properties'].keys():
    #                 logger.debug('Matching synonym found: {}'.format(synon))
    #                 return self.match_types(synon, field)

    def _match_types(self, InputField, OutputField):
        """
        Very stupid way to match fields' types
        """
        for k, v in InputField.items():
            InputField, inputStructure = k, v

        for k, v in OutputField.items():
            OutputField, outputStructre = k, v

        type = 'type'
        if type not in inputStructure and type not in outputStructre:
            logger.debug('Structure to Structure: {} to {}'.format(InputField, OutputField))
            if self._struct_cmp(inputStructure, outputStructre):
                return [self.find_path(InputField, self._PROCESSED_OUTPUT)[2],
                        self.find_path(OutputField, self._PROCESSED_INPUT)[2],
                        transforms.simple_pass.__name__]
            else:
                # przeszukaj rozniace sie struktury
                return self.transform(inputStructure, outputStructre)
                # return
        if type not in inputStructure and type in outputStructre:
            logger.debug('Field to Structure')
            return
        if type in inputStructure and type not in outputStructre:
            logger.debug('Structure to Field')
            return
        if inputStructure['type'] == outputStructre['type']:
            # logger.debug(InputField)
            return [self.find_path(InputField, self._PROCESSED_OUTPUT)[2],
                    self.find_path(OutputField, self._PROCESSED_INPUT)[2],
                    transforms.simple_pass.__name__]
        else:
            # logger.warning(InputField)
            method = '{}2{}'.format(inputStructure['type'], outputStructre['type'])
            try:
                return [self.find_path(InputField, self._PROCESSED_OUTPUT)[2],
                        self.find_path(OutputField, self._PROCESSED_INPUT)[2],
                        getattr(transforms, method).__name__]
            except AttributeError:
                raise NotImplementedError('{} transformation is not implemented yet!')

    def _struct_cmp(self, struct1, struct2):
        if struct1 == struct2:
            return True
        else:
            logger.warning('Differences in structures')
            return False

    def get_nested(self, my_dict, keys=[]):
        key = keys.pop(0)
        if len(keys) == 0:
            return my_dict[key]
        return self.get_nested(my_dict[key], keys)

    def generate_code(self):
        start = timer()
        try:
            inp = self._INPUT_SCHEMA['title'].replace(' ', '')
            out = self._OUTPUT_SCHEMA['title'].replace(' ', '')
        except Exception:
            logger.warning('Tried to generate code without schemas')
            return

        filling = list(self.transform(self._OUTPUT_SCHEMA['properties'], self._INPUT_SCHEMA['properties']))
        # logger.debug(filling)
        imports = list(set([trans[2] for trans in filling]))
        # logger.debug(imports)

        if len(filling) == 0:
            logger.debug('Nothing matched')
            return
        else:
            try:
                end = timer()
                logger.debug(f'Code generated in {end-start}!')
                return self._template.render(input_format=inp, output_format=out, filling=filling, imports=imports)
            except TypeError as e:
                logger.warning('Template must be set before generating service')

    def run_service(self):
        # A gdyby porty returnowac do flaska a stamtad przekierowywac na odpowiednie uslugi?
        import random
        from subprocess import Popen, CREATE_NEW_CONSOLE
        new_file = 'service_' + str(random.randint(100, 666)) + '.py'
        with open(new_file, 'w') as service_file:
            service_file.write(self.generate_code())
        Popen(['python', new_file], creationflags=CREATE_NEW_CONSOLE)

    # def RDF_subclass(self, thing):
    #     try:
    #         qres = self._USER_RDF.query("""SELECT ?label WHERE {
    #                                     ?Class rdfs:label "%s" .
    #                                     ?subClass rdfs:subClassOf ?Class .
    #                                     ?subClass rdfs:label ?label .
    #                                     }""" % thing.capitalize())
    #
    #         sub = ['%s' % row for row in qres]
    #         subclasses = [s.lower() for s in sub]
    #         # logger.debug(subclasses)
    #         return subclasses
    #     except AttributeError:
    #         logger.warning('RDF must be added before query')

    # def RDF_synonym(self, word):
    #     try:
    #         qres = self._USER_RDF.query("""SELECT ?label WHERE {
    #                                     ?Class rdfs:label "%s".
    #                                     ?Class rdfs:label ?label.
    #                                     }""" % word.capitalize())
    #
    #         syn = ['%s' % row for row in qres]
    #         synonyms = [s.lower() for s in syn]
    #         # logger.debug(synonyms)
    #         return synonyms
    #     except AttributeError:
    #         logger.warning('RDF must be added before query')

    def _process_dict(self, dictionary):
        pre_processed = list()
        for item in process_dict(dictionary):
            if item[0] in ('type', 'minimum', 'maximum', 'title', 'id', 'description', 'examples', 'default'):
                continue
            else:
                pre_processed.append(item)
        # remove duplicated paths
        processed = list()
        for record in pre_processed:
            # compare values under key in preprocessed dict and original
            if record[1] == dq(dictionary).get('/'.join(record[2])):
                processed.append(record)
            else:
                # remove record from list
                continue
        return processed

    def find_path(self, key, processed):
        for item in processed:
            if item[0] == key:
                return item

if __name__ == '__main__':
    fh = logging.FileHandler('generator.log')
    fh.setLevel(logging.DEBUG)
    # console = logging.StreamHandler()
    # console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-s:%(lineno)-14s: %(funcName)16s(): %(message)s')
    # console.setFormatter(formatter)
    fh.setFormatter(formatter)
    # logging.getLogger('').addHandler(console)
    logging.getLogger('').addHandler(fh)

    gen = JSONGenerator()
    gen.set_template_path()
    # gen.add_dictionary('../utils/rgb.csv')
    gen.load_rdf_from_file('../utils/colors.rdf')
    # gen.RDF_synonym()
    gen.load_schemas_from_file('../schema/rgb', '../schema/rgb2')
    print('INPUT:')
    for x in gen._PROCESSED_INPUT:
        print(x[:2], '/'.join(x[2]), '\n')
        # gen.RDF_synonym('Test2')

    print('OUTPUT:')
    for x in gen._PROCESSED_OUTPUT:
        print(x[:2], '/'.join(x[2]), '\n')


    # print(gen.find_path('deg', gen._PROCESSED_INPUT)[2])
    # print(gen.RDF_synonym('Red'))
    #
    # print(gen.RDF_subclass('Green'))

    # print(gen.generate_code())
        # gen.run_service()
