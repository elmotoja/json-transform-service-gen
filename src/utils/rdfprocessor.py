import rdflib
import logging

logger = logging.getLogger('RDF processor')
logger.setLevel(logging.DEBUG)


class RDFProcessor(object):
    """
    Class responsible for processing rdf file
    """
    def __init__(self):
        self._RDF = None
        logger.debug('{} created!'.format(self.__class__.__name__))

    def load_rdf_from_file(self, file_path, format='n3'):
        self._RDF = rdflib.Graph()
        self._RDF.parse(file_path, format=format)
        logger.debug(f'RDF loaded from path: {file_path}')

    def subclasses(self, thing):
        """
        Use this function to get 'thing' subclasses
        :param thing: 
        :return: List of subclasses based on rdf knowledge
        :rtype: list
        """
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
        """
        Use this function to get 'word' synonyms 
        :param word: 
        :return: List of synonyms based on rdf knowledge
        :rtype: list
        """
        try:
            qres = self._RDF.query("""SELECT ?label WHERE {
                                   ?Class rdfs:label "%s".
                                   ?Class rdfs:label ?label.
                                   }""" % word.capitalize())

            syn = ['%s' % row for row in qres]
            synonyms = [s for s in syn]
            return synonyms
        except AttributeError:
            logger.warning('RDF must be added before query')

    def possible_conversions(self, thing):
        """
        Use this function to get possible 'thing' transformations
        :param thing: 
        :return: Dictionary where keys are classes 'thing' can be transform and values are transformations names 
        :rtype: dict
        """
        try:
            # qres = self._RDF.query("""SELECT ?OtherLabel ?relLabel WHERE {
            #                        ?Class rdfs:label "%s" .
            #                        ?Class ?any ?OtherClass .
            #                        ?any rdfs:label ?relLabel .
            #                        ?OtherClass rdfs:label ?OtherLabel .
            #                        }""" % thing)
            qres = self._RDF.query("""SELECT ?label WHERE {
                                   ?Class rdfs:label "%s" .
                                   ?OtherClass ?any ?Class .
                                   ?OtherClass rdfs:label ?label .
                                   }""" % thing)

            trans = ['%s' % row for row in qres]
            transformations = [s for s in trans]

            return transformations
        except AttributeError:
            logger.warning('RDF must be added before query')

    def conversion(self, inField, outField):
        """
        Use this function to get possible 'thing' transformations
        :param thing: 
        :return: Dictionary where keys are classes 'thing' can be transform and values are transformations names 
        :rtype: dict
        """
        try:
            qres = self._RDF.query("""SELECT ?label WHERE {
                                  ?Class rdfs:label "%s" .
                                  ?InToClass rdfs:label "%s" .
                                  ?Class ?trans ?InToClass .
                                  ?trans rdfs:label ?label
                                  }""" % (outField, inField))

            trans = ['%s' % row for row in qres]
            transformations = [s for s in trans]
            return transformations
        except AttributeError:
            logger.warning('RDF must be added before query')

if __name__ == "__main__":
    test = RDFProcessor()
    test.load_rdf_from_file('../../rdf/pexample.rdf')

    temp = "AreaKM2"
    for possible in test.possible_conversions(temp):
        print(possible+" "+str(test.conversion(temp, possible)))

    for sub in test.subclasses(temp):
        print(sub)
