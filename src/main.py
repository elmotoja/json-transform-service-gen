from JSONGenerator import JSONGenerator
import sys
import getopt
import logging

console = logging.StreamHandler()
# console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(name)-14s: %(funcName)-22s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def config_default():
    gen = JSONGenerator()
    gen.set_template_path('../templates/python_service.py')
    return gen


def main(argv):
    gen = config_default()

    try:
        opts, args = getopt.getopt(argv, "hei:o:d:f:t:pr", ["ifile=", "ofile=", "--dictionary=",
                                                           "--template=", "--print", "--run", "--rdf="])
    except getopt.GetoptError as err:
        print(err.message)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt == '-e':
            gen.EXPERIMENTAL = True
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            gen.load_schemas_from_file(inputfile, outputfile)
        elif opt in ("-d", "--dictionary"):
            gen.add_dictionary(str(arg))
        elif opt in ("-f", "--rdf"):
            rdf_file_path = arg
            gen.load_rdf_from_file(rdf_file_path)
        elif opt in ("-t", "--template"):
            gen.set_template_path(str(arg))
        elif opt in ("-p", "--print"):
            print(gen.generate_code())
        elif opt in ("-r", "--run"):
            gen.run_service()

# SAMPLE CALLS
# nested dict
# py main.py - i../schema/nested - o../schema/nested2 - p

# ontology based conversion (USD, F -> PLN, C)
# py main.py -i ../schema/us_units -o ../schema/pl_units -f ../rdf/example.rdf -p

# transformation not implemented (KtoF)
# py main.py -i ../schema/tempK -o ../schema/tempF -f ../rdf/example.rdf -p

# ontology based synonyms match with some type transformations
# py main.py -i ../schema/rgb -o ../schema/rgb2 -f ../rdf/colors.rdf -p



# if __name__ == '__main__':
#     try:
#         gen.load_schemas_from_file(sys.argv[1], sys.argv[2])
#
#         # gen.dict.load_from_file('rgb.csv')
#         gen.add_dictionary('rgb.csv')
#         # print gen.dict
#         # gen.generate_code()
#         gen.transform()
#         print gen.generate_code()
#         # print gen.transform()
#         # gen.run_service()
#
#     except IndexError:
#         print 'no schema files defined!\n'

if __name__ == "__main__":
    main(sys.argv[1:])
