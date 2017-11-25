import rdflib
import logging

logger = logging.getLogger('RDF processor')
logger.setLevel(logging.DEBUG)


class RDFProcessor(object):
    def __init__(self):
        self._RDF = None
        logger.debug('{} created!'.format(self.__class__.__name__))

    def load_rdf_from_file(self, file_path, format='n3'):
        self._RDF = rdflib.Graph()
        self._RDF.parse(file_path, format=format)
        logger.debug(f'RDF loaded from path: {file_path}')

    def subclasses(self, thing):
        try:
            qres = self._RDF.query("""SELECT ?label WHERE {
                                        ?Class rdfs:label "%s" .
                                        ?subClass rdfs:subClassOf ?Class .
                                        ?subClass rdfs:label ?label .
                                        }""" % thing.capitalize())

            sub = ['%s' % row for row in qres]
            subclasses = [s.lower() for s in sub]
            return subclasses
        except AttributeError:
            logger.warning('RDF must be added before query')

    def synonyms(self, word):
        try:
            qres = self._RDF.query("""SELECT ?label WHERE {
                                   ?Class rdfs:label "%s".
                                   ?Class rdfs:label ?label.
                                   }""" % word.capitalize())

            syn = ['%s' % row for row in qres]
            synonyms = [s.lower() for s in syn]
            return synonyms
        except AttributeError:
            logger.warning('RDF must be added before query')