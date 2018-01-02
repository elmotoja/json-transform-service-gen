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

# label = "Temperature"
# qres = g.query("""SELECT ?label WHERE {
#                 ?Class rdfs:label "%s" .
#                ?subClass rdfs:subClassOf* ?Class .
#                ?subClass rdfs:label ?label .
#                }""" % label)

# res = g.query("""SELECT ?label WHERE {
#                 ?Class rdfs:label "TempC" .
#                 ?OtherClass ?any ?Class .
#                 ?OtherClass rdfs:label ?label .
#                 }""")

# print(['%s' % row for row in qres])
# ssubclasses = [s.lower() for s in sub]

res = g.query("""SELECT ?label WHERE {
              ?Class rdfs:label "TempC" .
              ?InToClass rdfs:label "TempF" .
              ?Class ?trans ?InToClass .
              ?trans rdfs:label ?label
              }""")

# for row in res:
#     print(list(row))
#     # print(row[1].toPython()+" | "+row[0].toPython()+" | "+row[2].toPython())
#     for elem in row:
#         print(elem)
for row in res:
    for elem in row:
        print(elem)