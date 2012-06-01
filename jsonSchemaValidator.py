#! /usr/bin/python
import simplejson as json
# python-validictory from repo
import validictory
import os

sampleData =  {
    "name": "recipeName", 
    "type": "regular",
    "build":
        {
        "targets":
            [
            'x86_64',
            'x86'
            ],
        
        "flavors":
            [
            {
                "flavor": 'bootstrap',
                "payload": ['bootstrap,!cross', 'cross,bootstrap']
                },
            { "flavor": '!bootstrap',
              'payload': ['!cross,!bootstrap']
              },
            ],
        },
    "source":
        {
        "homepage": "http://www.sas.com",
        "licensing": [ 'licFooOne',
                       'licFooTwo',
                       'licFooThree',
                       ],
        "tags": [ 'tagOne',
                  'tagTwo',
                  'tagThree',
                  ],
        "aliases": [ { "distro":"fedora",
                       "alias": "fedoraFoo"},
                     { "distro":"ubuntu",
                       "alias": "ubuntuFoo"},
                     ]
        },
    "packages":[
        {   "package": "pkgFoo",
            "licensing": [ 'licFooOne',],
            "aliases": [ { "distro":"fedora",
                           "alias": "fedoraFoo"},
                         { "distro":"ubuntu",
                           "alias": "ubuntuFoo"},
                         ],
            "tags": [ 'tagOne',
                      'tagTwo',
                      'tagThree',
                      ],
            "descriptions": [ 
                { "lang": 'en',
                  "summary": "Runtime libraries for foo",
                  "description": 'This package contains runtime libraries for use by foo:- the libfoo dynamic library, for use by applications that embed foo as a scripting language, and by the main "foo" executable - the foo standard library',
                  },
                { "lang": 'foo',
                  "summary": "...",
                  },

                ],
            
            },
        {   "package": "pkgFooBar",
            "licensing": [ 'licFooOne',],
            "aliases": [ { "distro":"fedora",
                           "alias": "fedoraFoo"},
                         { "distro":"ubuntu",
                           "alias": "ubuntuFoo"},
                         ],
            "tags": [ 'tagOne',
                      'tagTwo',
                      'tagThree',
                      ],
            "descriptions": [ 
                { "lang": 'en_US.utf8',
                  "summary": "Runtime libraries for foo",
                  "description": 'This package contains runtime libraries for use by foo:- the libfoo dynamic library, for use by applications that embed foo as a scripting language, and by the main "foo" executable - the foo standard library',
                  },
                { "lang": 'foo',
                  "summary": "...",
                  },

                ],
            
            },

        
        ],
    }



supportedFlavors = [ 'bootstrap',
                     '!bootstrap' ]
validFlavorsNames = { "type": "string",
                      "enum": supportedFlavors,
                      }
validFlavorsStrings = { "type": "string",}
validLicenseStrings = { "type": "string",}
validTagStrings = { "type": "string",}

validAliasPairs =  {
    "type":"object",
    "properties": {
        "alias":  { "type": "string" },
        "distro": { "type": "string" },
        "version": { "type": "string",
                     "required": False },
        },  
    }

validDescriptionSets = {
    "type":"object",
    "properties": {
        "lang": { "type": "string", },
        "summary":  {"type": "string"},
        "description":  { "type": "string",
                          "required": False },
        },  
    }

validPkgData = {
    "type":"object",
    "additionalProperties": False, 
    "properties": {
        "package": { "type" : "string"},
        "licensing":{ 
                      "required": False,
                      "items": validLicenseStrings,
                      "minItems": 1,
                      },
        "tags":{ 
                 "required": False,
                 "items": validTagStrings,
                 "minItems": 1,
                 },
        "aliases": { 
                     "required": False,
                     "items": validAliasPairs,
                     },
        "descriptions": { 
                          "items": validDescriptionSets,
                          "minItems": 1,
                          },
        },
    }

validFlavorPairs =  {
    "type":"object",
    "properties": {
        "flavor": validFlavorsNames,
        "payload": { 
                     "items": validFlavorsStrings 
                     },
        },  
    }
supportedArches = [ 'x86',
                    'x86_64', ]
validArches  = { "type": "string",
                 "enum": supportedArches,
                 }
supportedRecipeTypes = [ 'regular', 'superclass', 'factory', 
                         'info', 'redirect']
validRecipeTypes = { "type": "string",
                     "enum": supportedRecipeTypes,
                       }
schema = {
    "type": "object",
    "additionalProperties": False, 
    "properties":
        {
        "name":
            {
            "type" : "string",
            "required": True ,
            'readonly': True,
            },
        "type": validRecipeTypes,
        
        "build":
            {
            "type": "object",
            "additionalProperties": False, 
            "properties" :
                {
                "targets":
                    {
                    "items": validArches,
                    },
                "flavors":
                    {
                    "items": validFlavorPairs,
                    },
                },
            },
        "source":{
            "type": "object",
            "additionalProperties": False, 
            "properties":
                {
                "homepage":{ "type": "string",
                             "format": "uri",
                             },
                "licensing":
                    {
                    "items": validLicenseStrings,
                    "minItems": 1,
                    },
                "tags":
                    {
                    "items": validTagStrings,
                    "minItems": 1,
                    },
                "aliases":
                    { "items": validAliasPairs,
                      },
                },
            },
        "packages":
            {
            "items": validPkgData,
            },
        },
    }

def check_pkg(dir=os.getcwd()):
    pass
    

def create_template(force=False,dir=os.getcwd()):
    try:
        if os.path.exists (dir + "/" + os.path.basename(dir) + ".sauce") and force == False:
            print "file already exists\n"
    except IOError as e:
        print("({})".format(e))
        
def main():
    # validate sampleData according to our schema
    validictory.validate(sampleData, schema)
    check_pkg()
    create_template(dir="/tmp")
    # print json.dumps(schema, indent=4, sort_keys=True)
    #print json.dumps(sampleData, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()
