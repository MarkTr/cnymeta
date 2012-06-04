import argparse
import validictory
import jsonSchemaValidator as jSV



def defineArgs():
    parser = argparse.ArgumentParser('Create and modify metafiles')
    parser.add_argument("-n", action="store_true", default=False, help="Create new metafile")
    parser.add_argument("-d", action="store", dest="dir", help="create template here instead of pwd")
    parser.add_argument("-f", action="store_true", default=False, help="Overwrite existing files")
    parser.add_argument("--add-src", action="append", dest="src", help="add data", nargs=1)
    parser.add_argument("--add-pkg", action="append", dest="pkg", nargs='+')

    print parser.parse_args()

def main():
    defineArgs()
    # validate sampleData according to our schema
    validictory.validate(jSV.sampleData, jSV.schema)
    jSV.check_pkg()
    jSV.create_template()
    # print json.dumps(schema, indent=4, sort_keys=True)
    #print json.dumps(sampleData, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()
