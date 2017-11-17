import json
import logging
import sys

import rdflib
from jinja2 import Environment, FileSystemLoader
from nested_lookup import nested_lookup

from src import transforms
from .synonymdict import SynonymDict

# def ObjectFromSchemaFactory(schema):
#     builder = pjs.ObjectBuilder(schema)
#     clasessRepository = builder.build_classes()
#     return clasessRepository

logger = logging.getLogger('Generator')
logger.setLevel(logging.DEBUG)


# import PyDictionary


# import python_jsonschema_objects as pjs
# TODO: Nested dicts support

class JSONGenerator:
    def __init__(self):
        self._template = None
        self._INPUT_SCHEMA = {}
        self._OUTPUT_SCHEMA = {}
        self._USER_DICT = None  # SynonymDict()
        self._USER_RDF = None
        logger.debug('{} created!'.format(self.__class__.__name__))

    def set_template_path(self, file_path='../templates/python_service.py'):
        template_folder_path = '/'.join(file_path.split('/')[:-1])
        template_file = file_path.split('/')[-1]
        env = Environment(loader=FileSystemLoader(template_folder_path))
        logger.debug('Template loaded from path: {}'.format(file_path))
        self._template = env.get_template(template_file)

    def add_dictionary(self, file_path):
        self._USER_DICT = SynonymDict()
        self._USER_DICT.load_from_file(file_path)

    def load_rdf_from_file(self, file_path, format='n3'):
        self._USER_RDF = rdflib.Graph()
        self._USER_RDF.parse(file_path, format=format)
        logger.debug('RDF loaded from path: {}'.format(file_path))

    def load_rdf_from_url(self):
        raise NotImplementedError('Function not implemented yet!')

    def load_schemas_from_file(self, input_schem, output_schem):
        with open(input_schem, 'r') as inFile, \
                open(output_schem, 'r') as outFile:
            self._INPUT_SCHEMA = json.loads(inFile.read())
            self._OUTPUT_SCHEMA = json.loads(outFile.read())

    def load_schemas_from_url(self):
        raise NotImplementedError('Function not implemented yet!')

    def transform(self, target_structure, given_structure):

        matches = []
        # logger.debug(target_structure)
        for field in target_structure.keys():
            # matches.append(self.match_transformation(field))
            if field in given_structure.keys():
                logger.debug('{0} matched to {0}'.format(field))
                matches.append(self._match_types({field: target_structure[field]},
                                                 {field: given_structure[field]}))
            else:
                if self._USER_DICT:
                    logger.debug('Property \'{}\' not found.'
                                 ' Known synonyms: {}'.format(field, str(self._USER_DICT.synonyms(field)[field])))
                    for synon in self._USER_DICT.synonyms(field)[field]:
                        if synon in given_structure.keys():
                            logger.debug('Matching synonym found: {}'.format(synon))
                            matches.append(self._match_types({field: target_structure[field]},
                                                             {synon: given_structure[synon]}))
            if self._USER_RDF:
                logger.debug('Property \'{}\' not found.'
                             ' Known subclasses: {}'.format(field, str(self.RDF_subclass(field))))
                for subclass in self.RDF_subclass(field):
                    if subclass in given_structure.keys():
                        logger.debug('Matching subclass found: {}'.format(subclass))
                        matches.append(self._match_types(subclass, field))
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
        # inputStructure = self._INPUT_SCHEMA['properties'][InputField]
        # outputStructre = self._OUTPUT_SCHEMA['properties'][OutputField]
        # logger.warning(list(InputField))
        # inputStructure = InputField[list(InputField)[0]]
        # InputField = list(InputField.keys())
        # InputField, inputStructure = InputField.items()
        for k, v in InputField.items():
            InputField, inputStructure = k, v

        for k, v in OutputField.items():
            OutputField, outputStructre = k, v

        # outputStructre = OutputField[list(OutputField)[0]]
        # OutputField = list(OutputField.keys())

        type = 'type'

        if type not in inputStructure and type not in outputStructre:
            logger.debug('Structure to Structure: {} to {}'.format(InputField, OutputField))
            if self._struct_cmp(inputStructure, outputStructre):
                return [InputField, OutputField, transforms.simple_pass.__name__]
            else:
                # przeszukaj rozniace sie struktury
                # return self.transform(inputStructure, outputStructre)
                return None
        if type not in inputStructure and type in outputStructre:
            logger.debug('Field to Structure')
            return None
        if type in inputStructure and type not in outputStructre:
            logger.debug('Structure to Field')
            return None
        if inputStructure['type'] == outputStructre['type']:
            return [InputField, OutputField, transforms.simple_pass.__name__]
        else:
            # logger.warning(InputField)
            method = '{}2{}'.format(inputStructure['type'], outputStructre['type'])
            try:
                return [InputField, OutputField, getattr(transforms, method).__name__]
            except AttributeError:
                raise NotImplementedError('{} transformation is not implemented yet!')

    def generate_code(self):
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
                logger.debug('Code generated!')
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

    def RDF_subclass(self, thing):
        try:
            # prefix = "tmp"
            # thing_with_prefix = ':'.join((prefix, thing.capitalize()))
            # logger.debug('RDF query for: {}'.format(thing_with_prefix))

            # qres = self._USER_RDF.query(
            #     """SELECT ?label WHERE {
            #     ?subClass rdfs:subClassOf* %s .
            #     ?subClass rdfs:label ?label .
            #        }""" % thing_with_prefix)

            qres = self._USER_RDF.query(
                 'SELECT ?label WHERE {' +
                 f'?Class rdfs:label {thing} .' +
                 '?subClass rdfs:subClassOf* ?Class .' +
                 '?subClass rdfs:label ?label}')

            sub = ['%s' % row for row in qres]
            subclasses = [s.lower() for s in sub]
            # logger.debug(subclasses)
            return subclasses
        except AttributeError:
            logger.warning('RDF must be added before query')

    def RDF_synonym(self):
        qres = self._USER_RDF.query(
            """SELECT ?label WHERE {
            ?label rdfs:label* %s.
               }""" % "tmp:Temperature")
        synonyms = ['%s' % row for row in qres]
        logger.debug(synonyms)
        return synonyms

    def _struct_cmp(self, struct1, struct2):
        if struct1 == struct2:
            return True
        else:
            logger.warning('Differences in structures')
            return False


if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-s:%(lineno)-14s: %(funcName)16s(): %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    gen = JSONGenerator()
    gen.set_template_path()
    gen.add_dictionary('rgb.csv')
    # gen.load_rdf_from_file('temperature.rdf')
    # gen.RDF_synonym()
    gen.load_schemas_from_file(sys.argv[1], sys.argv[2])
    print(gen.generate_code())
    # gen.run_service()
