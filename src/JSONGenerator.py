import json
import logging
from synonymdict import SynonymDict
from jinja2 import Environment, FileSystemLoader

# def ObjectFromSchemaFactory(schema):
#     builder = pjs.ObjectBuilder(schema)
#     clasessRepository = builder.build_classes()
#     return clasessRepository
import transforms

logger = logging.getLogger('Generator')
logger.setLevel(logging.DEBUG)

import PyDictionary


# import python_jsonschema_objects as pjs
# TODO rdflib

class JSONGenerator:
    def __init__(self):
        self.template = None
        self.INPUT_SCHEMA = {}
        self.OUTPUT_SCHEMA = {}
        self.dict = SynonymDict()
        logger.debug('{} created!'.format(self.__class__.__name__))

    def set_template_path(self, file_path='../templates/service_template.py'):
        template_folder_path = '/'.join(file_path.split('/')[:-1])
        template_file = file_path.split('/')[-1]
        # logging.debug(file_path)
        env = Environment(loader=FileSystemLoader(template_folder_path))
        self.template = env.get_template(template_file)

    def add_dictionary(self, file_path):
        self.dict.load_from_file(file_path)

    def load_schemas_from_file(self, input_schem, output_schem):
        with open(input_schem, 'r') as inFile, \
                open(output_schem, 'r') as outFile:
            self.INPUT_SCHEMA = json.loads(inFile.read())
            self.OUTPUT_SCHEMA = json.loads(outFile.read())

    def load_schemas_from_url(self):
        raise NotImplementedError

    def transform(self,target_structure, given_structure):

        matches = []
        for field in self.OUTPUT_SCHEMA['properties'].keys():
            matches.append(self.match_transformation(field))
        # print matches
        return filter(None, matches)

    def match_transformation(self, field):
        from jsonschema import validate
        if field in self.INPUT_SCHEMA['properties'].keys():
            logger.debug('{0} matched to {0}'. format(field))
            # or field is synonym of any of output keys
            # if self.INPUT_SCHEMA['properties'][field]['type'] \
            #         == self.OUTPUT_SCHEMA['properties'][field]['type']:
            if self.match_types(self.INPUT_SCHEMA['properties'][field],
                                self.OUTPUT_SCHEMA['properties'][field]):
                return [field, field, transforms.simple_pass.__name__]
            else:
                method = '{}2{}'.format(self.INPUT_SCHEMA['properties'][field]['type'],
                                        self.OUTPUT_SCHEMA['properties'][field]['type'])
                try:
                    return [field, field, getattr(transforms, method).__name__]
                except AttributeError:
                    raise NotImplementedError('{} transformation is not implemented yet!'.format(method))
        else:
            logger.debug('Property \'{}\' not found. Known synonyms: {}'.format(field,
                                                                                str(self.dict.synonyms(field)[field])))
            for synon in self.dict.synonyms(field)[field]:
                if synon in self.INPUT_SCHEMA['properties'].keys():
                    logger.debug('Matching synonym found: {}'.format(synon))
                    if self.match_types(self.INPUT_SCHEMA['properties'][synon],
                                        self.OUTPUT_SCHEMA['properties'][field]):
                        return [synon, field, transforms.simple_pass.__name__]
                    else:
                        method = '{}2{}'.format(self.INPUT_SCHEMA['properties'][synon]['type'],
                                                self.OUTPUT_SCHEMA['properties'][field]['type'])
                        try:
                            return [synon, field, getattr(transforms, method).__name__]
                        except AttributeError:
                            raise NotImplementedError('{} transformation is not implemented yet!'.format(method))

    # def match_types(self, one_field, scnd_field):
    #     try:
    #         if one_field['type'] == scnd_field['type']:
    #             same_types = True
    #         else:
    #             same_types = False
    #     except KeyError:

    def match_types(self, InputField, OutputField):
        """
        Very stupid way to match fields' types
        """
        type = 'type'
        if type not in InputField and type not in OutputField:
            logger.debug('Structure to Structure')
            return 'sts'
        if type not in InputField and type in OutputField:
            logger.debug('Field to Structure')
            return 'fts'
        if type in InputField and type not in OutputField:
            logger.debug('Structure to Field')
            return 'stf'
        if InputField['type'] == OutputField['type']:
            return True
        else:
            return False

    def generate_code(self):
        try:
            inp = self.INPUT_SCHEMA['title'].replace(' ', '')
            out = self.OUTPUT_SCHEMA['title'].replace(' ', '')
        except Exception:
            logger.warning('Tried to generate code without schemas')

        filling = self.transform()
        imports = list(set([trans[2] for trans in filling]))

        if len(filling) != 0:
            logger.debug('Code generated!')
            return self.template.render(input_format=inp, output_format=out, filling=filling, imports=imports)
        else:
            return []

    def run_service(self):
        # A gdyby porty returnowac do flaska a stamtad przekierowywac na odpowiednie uslugi?
        import random
        from subprocess import Popen, CREATE_NEW_CONSOLE
        new_file = 'service_' + str(random.randint(100, 666)) + '.py'
        with open(new_file, 'w') as service_file:
            service_file.write(self.generate_code())
        # exec cmd command
        # call(['python', new_file])
        Popen(['python', new_file], creationflags=CREATE_NEW_CONSOLE)

if __name__ == '__main__':
    gen = JSONGenerator()
    # gen.load_schemas(sys.argv[1], sys.argv[2])
    # print gen.generate_code()
    # gen.run_service()
