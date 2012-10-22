# -*- coding: utf-8 -*-
import lxml.etree as et
import os
import sys

class MetaData:
    def __init__(self, sauce=None, createTemplate=False):
        if not sauce or sauce == "":
            path = os.getcwd().rstrip('/') 
            name = os.path.basename(path)
            sauce = path +'/' + name + ".sauce"
        if not createTemplate and not os.path.isfile(sauce):
            sys.exit ('saucefile does not exist')
        self.sauce=sauce
        self.mapData(createTemplate=createTemplate)
    
    def mapData(self,createTemplate=False):
        if not createTemplate:
            self.tree = et.parse(self.sauce)
            self.root = self.tree.getroot()
        else:
            self.tree = et.ElementTree(et.XML("<recipe></recipe>"))
            self.root = self.tree.getroot()
            self.root.set('type', 'default')
            
        self.recipeType = self.root.attrib['type']
        self.source = Source(self.root)
        self.flavors = Flavors(self.root)
        self.targets = Targets(self.root)
        self.packages = Packages(self.root)
    
    def write(self):
        tree = et.ElementTree(et.XML("<recipe></recipe>"))
        root = tree.getroot()
        root.set('type', self.recipeType)
        
        # source
        source = et.SubElement(root,"source")
        
        homepage=et.SubElement(source,"homepage")
        homepage.text=self.source.homepage
        
        self._createLicensing(self.source.licenses,source)
        
        self._createTags(self.source.tags,source)
            
        self._createAliases(self.source.aliases,source)
        
        # Flavors
        flavors=et.SubElement(root,'flavors')
        for k in self.flavors.flavor:
            flavor=et.SubElement(flavors,'flavor',attrib={'name':k})
            for e in self.flavors.flavor[k]:
                f=et.SubElement(flavor,'flavoring')
                f.text=e
        
        # Targets
        targets=et.SubElement(root,'targets')
        for k in self.targets.target:
            t=et.SubElement(targets,'target',attrib={'arch':k})
            t.text=self.targets.target[k]
            
        # packages
        packages=et.SubElement(root,'packages')
        for k in self.packages.package:
            p=et.SubElement(packages,'package',{'name':k})
            package=self.packages.package[k]
            self._createLicensing(package.licenses,p)
            self._createAliases(package.aliases,p)
            self._createTags(package.tags,p)
            descriptions=et.SubElement(p,'description')
            for lang in package.descriptions:
                l=et.SubElement(descriptions,'locale',{'lang':lang})
                locale=package.descriptions[lang]
                for i in locale:
                    e=et.SubElement(l,i)
                    e.text=locale[i]
                    
        self.tree=tree
        self.root=root

        self.tree.write(self.sauce, encoding="utf-8", pretty_print=True, xml_declaration=True)
        
    def _createLicensing(self,licenses,parent):
        licensing=et.SubElement(parent,"licensing")
        for l in licenses:
            le = et.SubElement(licensing,"license")
            le.text=l
            
    def _createAliases(self,aliases,parent):
        al=et.SubElement(parent,'aliases')
        for k in aliases:
            a=et.SubElement(al,'alias',attrib={'distro':k})
            a.text=aliases[k]
            
    def _createTags(self,tags,parent):
        t=et.SubElement(parent,"tags")
        for tag in tags:
            te = et.SubElement(t,"tag")
            te.text=tag

            
class Source:
    def __init__(self,root):
        self._initHomepage(root)
        self._initLicenses(root)
        self._initTags(root)
        self._initAliases(root)
        
    def _initHomepage(self,root):
        e = root.find('source/homepage')
        self.homepage = e.text if e is not None else ""
            
    def _initLicenses(self,root):
        self.licenses=[]
        p = root.find('source/licensing')
        if p is None: return
        for e in p.getchildren():
            self.licenses.append(e.text)
    
    def _initTags(self,root):
        self.tags=[]
        p = root.find('source/tags')
        if p is None: return
        for e in p.getchildren():
            self.tags.append(e.text)

    def _initAliases(self,root):
        self.aliases={}
        p = root.find('source/aliases')
        if p is None: return
        for e in p.getchildren():
            self.aliases[e.attrib['distro']] = e.text
 
class Flavors:
    def __init__(self,root):
        self.flavor = {}
        p = root.findall('flavors/flavor')
        if p is None: return
        for e in p:
            flavoring = []
            for f in e.getchildren():
                flavoring.append(f.text)
            self.flavor[e.attrib['name']] = flavoring
            
            
class Targets:
    def __init__(self,root):
        self.target = {}
        p = root.find('targets')
        if p is None: return
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
    
