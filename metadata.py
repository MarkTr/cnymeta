# -*- coding: utf-8 -*-
import lxml.etree as et
import os
import sys

class MetaData:
    def __init__(self, sauce=None):
        if not sauce or sauce == "":
            path = os.getcwd().rstrip('/') 
            name = os.path.basename(path)
            sauce = path +'/' + name + ".sauce"
        if not os.path.isfile(sauce):
            sys.exit ('saucefile does not exist')
        self.sauce=sauce
        self.tree = et.parse(sauce)
        self.root = self.tree.getroot()
        self.recipeType = self.root.attrib['type']
        self.source = Source(self.root)
        self.flavors = Flavors(self.root)
        self.targets = Targets(self.root)
        self.packages = Packages(self.root)
        
class Source:
    def __init__(self,root):
        self._initHomepage(root)
        self._initLicenses(root)
        self._initTags(root)
        self._initAliases(root)
        
    def _initHomepage(self,root):
        e = root.find('source/homepage')
        self.homepage = e.text
            
    def _initLicenses(self,root):
        self.licenses=[]
        p = root.find('source/licensing')
        for e in p.getchildren():
            self.licenses.append(e.text)
    
    def _initTags(self,root):
        self.tags=[]
        p = root.find('source/tags')
        for e in p.getchildren():
            self.tags.append(e.text)

    def _initAliases(self,root):
        self.aliases={}
        p = root.find('source/aliases')
        for e in p.getchildren():
            self.aliases[e.attrib['distro']] = e.text
 
class Flavors:
    def __init__(self,root):
        self.flavor = {}
        p = root.findall('flavors/flavor')
        for e in p:
            flavoring = []
            for f in e.getchildren():
                flavoring.append(f.text)
            self.flavor[e.attrib['name']] = flavoring
            
            
class Targets:
    def __init__(self,root):
        self.target = {}
        p = root.find('targets')
        for e in p:
            self.target[e.attrib['arch']] = e.text
        
class Packages:
    def __init__(self,root):
        self.package={}
    
        for e in root.findall('packages/package'):
            name=e.attrib['name']
            licenses=[]
            aliases={}
            tags=[]
            descriptions={}
            
            for c in e.getchildren():
                if c.tag=='licensing':
                    for l in c.getchildren():
                        licenses.append(l.text)
                if c.tag=='aliases':
                    for a in c.getchildren():
                      aliases[a.attrib["distro"]] = a.text
                if c.tag=='tags':
                    for t in c.getchildren():
                        tags.append(t.text)
                if c.tag=='descriptions':
                    for d in c.getchildren():
                        locale={}
                        for l in d.getchildren():
                            locale[l.tag]=l.text
                        descriptions[d.attrib['lang']]=locale
                    
            self.package[name] = Packages.Package(name=name, licenses=licenses, 
                aliases=aliases, tags=tags, descriptions=descriptions)
                
    class Package:
        def __init__(self, name="", licenses=[], aliases={},tags=[], descriptions={}):
            self.name=name
            self.licenses=licenses
            self.aliases=aliases
            self.tags=tags
            self.descriptions=descriptions
    
