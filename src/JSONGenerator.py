import json
import logging
import sys

import rdflib
from jinja2 import Environment, FileSystemLoader

from synonymdict import SynonymDict
from utils.schema import Schema
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

class JSONGenerator:
    """Main generator class"""
    def __init__(self):
        self._template = None
        self._INPUT_SCHEMA = None
        self._OUTPUT_SCHEMA = None
        self._USER_DICT = None  # SynonymDict()
        self._USER_RDF = None
        logger.debug('{} created!'.format(self.__class__.__name__))
        self.EXPERIMENTAL = False

    def set_template_path(self, file_path='../templates/python_service.py'):
        """Use this function to set template path
        :param file_path: path to service template file
        :return: 
        """
        template_folder_path = '/'.join(file_path.split('/')[:-1])
        template_file = file_path.split('/')[-1]
        env = Environment(loader=FileSystemLoader(template_folder_path))
        logger.debug(f'Template loaded from path: {file_path}')
        self._template = env.get_template(template_file)

    def add_dictionary(self, file_path):
        """Use this function to add user dictionary
        :param file_path: path to csv file 
        :return: 
        """
        self._USER_DICT = SynonymDict()
        self._USER_DICT.load_from_file(file_path)

    def load_rdf_from_file(self, file_path, format='n3'):
        """Use this function to load user rdf file 
        :param file_path: path to rdf file
        :param format: optional param to set rdf format, default=n3
        :return: 
        """
        self._USER_RDF = RDFProcessor()
        self._USER_RDF.load_rdf_from_file(file_path, format=format)

    def load_rdf_from_url(self):
        raise NotImplementedError('Function not implemented yet!')

    def load_schemas_from_file(self, input_schem, output_schem):
        """Use this function to load schema files from paths
        :param input_schem: Path to input schema file
        :param output_schem: Path to output schema file
        :return: 
        """
        with open(input_schem, 'r') as inFile:
            self._INPUT_SCHEMA = Schema(json.loads(inFile.read()), slice='properties')
            logger.debug(f'Input schema loaded from: {input_schem}')
        with open(output_schem, 'r') as outFile:
            self._OUTPUT_SCHEMA = Schema(json.loads(outFile.read()), slice='properties')
            logger.debug(f'Output schema loaded from: {output_schem}')

    def load_schemas_from_url(self, input_url, output_url):
        """
        Use this function to load schemas from web
        :param input_url: Input schema URL
        :param output_url: Output schema URL
        :raise NotImplementedError:
        """
        try:
            self._INPUT_SCHEMA.load_schema_from_url(input_url)
            self._OUTPUT_SCHEMA.load_schema_from_url(output_url)
        except NotImplementedError as e:
            logger.warning(f'{e}')

    def transform(self, target_structure, given_structure, *, root=None):
        """Function used to match fields from given structure to target structure
        :param target_structure: 
        :param given_structure: 
        :param root: 
        :return: List of matched fields with transformationsqui
        """
        logger.debug(f'Matching : {target_structure.keys()} to {given_structure.keys()}')
        matches = list()
        matched_paths = list()
        for field in target_structure.keys():
            if field in given_structure.keys():
                logger.debug(f'Property \'{field}\' found.')
                if root: logger.debug(f'Property \'{field}\' found. w/ {root}')
                match = self._match_types((field, target_structure[field]),
                                          (field, given_structure[field]), root=root)
                matches.append(match)
                # matched_paths.append(match[1])
                # logger.debug(match)
                continue
            else:
                logger.debug(f'Property \'{field}\' not found.')
                if self._USER_DICT:
                    replacements = self._USER_DICT.replacements(field)[field]
                    logger.debug(f'Known replacements: {str(replacements)}')
                    for replacement in replacements:
                        if replacement in given_structure.keys():
                            logger.debug(f'Matching replacement found: {replacement}')
                            matches.append(self._match_types((field, target_structure[field]),
                                                             (replacement, given_structure[replacement]), root=root))
                    continue
            if self._USER_RDF:
                synonyms = self._USER_RDF.synonyms(field)
                logger.debug(f'Known synonyms: {str(synonyms)}')
                for synonym in synonyms:
                    if synonym in given_structure.keys():
                        logger.debug(f'Matching synonym found: {synonym}')
                        matches.append(self._match_types((field, target_structure[field]),
                                                         (synonym, given_structure[synonym]), root=root))
                    continue
                subclasses = self._USER_RDF.subclasses(field)
                logger.debug(f'Known subclasses: {str(subclasses)}')
                for subclass in subclasses:
                    if subclass in given_structure.keys():
                        logger.debug(f'Matching subclass found: {subclass}')
                        matches.append(self._match_types((field, target_structure[field]),
                                                         (subclass, given_structure[subclass]), root=root))
                    continue
        return filter(None, matches)

    def _match_types(self, InputField, OutputField, *, root=None):
        """
        Very stupid way to match fields types
        """

        InputField, inputStructure = InputField
        OutputField, outputStructre = OutputField

        type = 'type'
        if type not in inputStructure and type not in outputStructre:
            logger.debug(f'Structure to Structure: {InputField} to {OutputField}')
            if self._struct_cmp(inputStructure, outputStructre):
                return [self._OUTPUT_SCHEMA.path(InputField),
                        self._INPUT_SCHEMA.path(OutputField),
                        transforms.simple_pass.__name__]
            else:
                # przeszukaj rozniace sie struktury
                if self.EXPERIMENTAL:
                    logger.debug(
                        f'Inner transformation:\n{InputField}: {inputStructure}\n{OutputField}: {outputStructre}')
                    return list(self.transform(inputStructure, outputStructre, root=InputField))
                return
        if type not in inputStructure and type in outputStructre:
            logger.warning('Field to Structure')
            return
        if type in inputStructure and type not in outputStructre:
            logger.warning('Structure to Field')
            return
        if inputStructure['type'] == outputStructre['type']:
            return [self._OUTPUT_SCHEMA.path(InputField),
                    self._INPUT_SCHEMA.path(OutputField, root=root),
                    transforms.simple_pass.__name__]
        else:
            method = f'{inputStructure[type]}2{outputStructre[type]}'
            try:
                return [self._OUTPUT_SCHEMA.path(InputField),
                        self._INPUT_SCHEMA.path(OutputField, root=root),
                        getattr(transforms, method).__name__]
            except AttributeError:
                raise NotImplementedError(f'{method} transformation is not implemented yet!')

    def _struct_cmp(self, struct1, struct2):
        """
        Helper function to compare dicts
        :param struct1: Dict1
        :param struct2: Dict2
        :return: True, if Dict1 == Dict2, False if not
        :rtype: Boolean
        """
        if struct1 == struct2:
            return True
        else:
            logger.warning('Differences in structures')
            return False

    def generate_code(self):
        """
        Function fill loaded template
        :return: 
        :raise: Exception
        """
        try:
            inp = self._INPUT_SCHEMA.as_dict()['title'].replace(' ', '')
            out = self._OUTPUT_SCHEMA.as_dict()['title'].replace(' ', '')
        except Exception:
            logger.warning('Tried to generate code without schemas')
            return

        filling = list(self.transform(self._OUTPUT_SCHEMA, self._INPUT_SCHEMA))
        logger.debug(filling)
        imports = list(set([trans[2] for trans in filling]))
        # logger.debug(imports)

        if len(filling) == 0:
            logger.debug('Nothing matched')
            return
        else:
            try:
                logger.debug(f'Code generated!' + "\n" * 2)
                return self._template.render(input_format=inp, output_format=out, filling=filling, imports=imports)
            except TypeError as e:
                logger.warning('Template must be set before generating service')

    def run_service(self):
        """
        Experimental function that generate code and run service
        :return: 
        """
        # A gdyby porty returnowac do flaska a stamtad przekierowywac na odpowiednie uslugi?
        import random
        from subprocess import Popen, CREATE_NEW_CONSOLE
        new_file = f'service_{str(random.randint(100, 666))}.py'
        with open(new_file, 'w') as service_file:
            service_file.write(self.generate_code())
        Popen(['python', new_file], creationflags=CREATE_NEW_CONSOLE)


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
    gen.load_rdf_from_file('../rdf/colors.rdf')
    # gen.RDF_synonym()
    gen.load_schemas_from_file('../schema/air_temperature', '../schema/temperature')
    print(gen.generate_code())

    # print(gen.find_path('deg', gen._PROCESSED_INPUT)[2])
    # print(gen.RDF_synonym('Red'))
    #
    # print(gen.RDF_subclass('Green'))

    # print(gen.generate_code())
    # gen.run_service()
