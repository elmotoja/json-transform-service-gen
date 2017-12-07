import rdflib

g = rdflib.Graph()
g.parse('temperature.rdf', format='n3')


# qres = g.query(
#     """SELECT ?Class WHERE {
#     ?Class rdfs:label "%s" .
#        }""" % label)

#    ?subClass rdfs:subClassOf* ?Class .
#     ?subClass rdfs:label ?label .
#  % 'Air_temperature'

label = "Temperature"
thing = "cos"
qres = g.query("""SELECT ?label WHERE {
                ?Class rdfs:label "%s" .
               ?subClass rdfs:subClassOf* ?Class .
               ?subClass rdfs:label ?label .
               }""" % label)
print(['%s' % row for row in qres])
# ssubclasses = [s.lower() for s in sub]
