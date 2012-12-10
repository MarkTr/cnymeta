# -*- coding: utf-8 -*-
import lxml.etree as et
import os
import sys
import string

class MetaData:
    def __init__(self, sauce=None, createTemplate=False, recipeType='default'):
        if not sauce or sauce == "":
            path = os.getcwd().rstrip('/') 
            self.name = os.path.basename(path)
            sauce = path +'/' + self.name + ".sauce"
        else:
            self.name = os.path.basename(sauce).split('.')[0]
        if not createTemplate and not os.path.isfile(sauce):
            sys.exit ('saucefile does not exist')
        self.sauce=sauce
        self.mapData(createTemplate=createTemplate,recipeType=recipeType)
    
    def mapData(self,createTemplate=False, recipeType='default'):
        if not createTemplate:
            self.tree = et.parse(self.sauce)
            self.root = self.tree.getroot()
        else:
            self.tree = et.ElementTree(et.XML("<recipe></recipe>"))
            self.root = self.tree.getroot()
            self.root.set('type', recipeType)
            
        self.recipeType = self.root.attrib['type']
        self.source = Source(self.root)
        if recipeType=='default':
            self.flavors = Flavors(self.root)
            self.targets = Targets(self.root)
            self.packages = Packages(self.root)
        
        if createTemplate==True:
            if recipeType=='default':
                self.update('flavor', "!bootstrap", "!bootstrap")
                self.update('target', None,'x86')
                self.update('target', None, 'x86_64')
                self.update('package', self.name+':'+'name',self.name)
            else:
                self.update('source','homepage','http://www.foresightlinux.org')

    def update(self, scope, tag, value):
        if scope=='source':
            self.source.update(tag=tag, value=value)
        if scope=='flavor':
            self.flavors.update(tag=tag, value=value)
        if scope=='target':
            self.targets.update(tag=tag, value=value)
        if scope=='package':
            self.packages.update(tag=tag, value=value)
        if scope=='recipe':
            if tag=='type':
                self.recipeType=value
        
    def remove(self, scope, tag, value=None):
        if scope=='source':
            self.source.remove(tag=tag, value=value)
        if scope=='flavor':
            self.flavors.remove(tag=tag, value=value)
        if scope=='target':
            self.targets.remove(tag=tag, value=value)
        if scope=='package':
            self.packages.remove(tag=tag, value=value) 

    def show(self,scope=None,tag=None):
        if scope=='recipe' or scope==None:
            print 'recipeType', self.recipeType
        if scope=='source' or scope==None: # TODO: there must be a more clever way
            self.source.show(tag)
        if scope=='flavor' or scope==None:
            self.flavors.show(tag)
        if scope=='target' or scope==None:
            self.targets.show(tag)
        if scope=='package' or scope==None:
            self.packages.show(tag)

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
        
        if self.recipeType=='default':        
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
                t=et.SubElement(targets,'target')
                t.text=k
                
            # packages
            packages=et.SubElement(root,'packages')
            for k in self.packages.package:
                p=et.SubElement(packages,'package',{'name':k})
                package=self.packages.package[k]
                self._createLicensing(package.licenses,p)
                self._createAliases(package.aliases,p)
                self._createTags(package.tags,p)
                descriptions=et.SubElement(p,'descriptions')
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
            
    def update(self, tag, value):
        if tag=='tag':
            self.tags.append(value)
        if tag=='homepage':
            self.homepage=value
        if tag=='alias':
            data=value.split(':')
            self.aliases[data[0]]=data[1]
        if tag=='license':
            if value not in self.licenses:
                self.licenses.append(value)
            
    def remove(self, tag, value=None):
        if tag=='tag':
            self.tags.remove(value)
        if tag=='homepage':
            self.homepage=""
        if tag=='alias':
            data=value.split(':')
            del self.aliases[data[0]]
        if tag=='license':
            self.licenses.remove(value)

    def show(self, tag):
        if tag=='tag' or tag==None:
            print 'Tags', self.tags
        if tag=='homepage' or tag==None:
            print 'Homepage', self.homepage
        if tag=='alias' or tag==None:
            print 'Aliases', self.aliases
        if tag=='license' or tag==None:
            print 'Licenses', self.licenses
 
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

    def update(self, tag, value):
        if tag in self.flavor:
            self.flavor[tag].append(value)
        else:
            self.flavor[tag]=[value]
        
    def remove(self, tag, value=None):
        self.flavor[tag].remove(value)
        
    def show(self,tag):
        print 'Flavors', self.flavor
            
class Targets:
    def __init__(self,root):
        self.target = []
        p = root.find('targets')
        if p is None: return
        for e in p:
            self.target.append(e.text)

    def update(self, tag, value):
        if value not in self.target:
            self.target.append(value)
        
    def remove(self, tag, value=None):
        if value in self.target:
            self.target.remove(value)
            
    def show(self,tag):
        print 'Targets', self.target

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

    def update(self, tag, value):
        tag=tag.split(':',1)
        if tag[0] not in self.package:
            self.package[tag[0]]=Packages.Package(name=tag[0])
        if len(tag)>1:    
            self.package[tag[0]].update(tag[1], value)
            
        
    def remove(self, tag, value=None):
        tag=tag.split(':',1)
        if len(tag)==1:
            del self.package[tag[0]]
        else:
            self.package[tag[0]].remove(tag[1],value)
        
    def show(self,tag):
        if tag is not None:
            splittag=tag.split(':',1)
        if tag is not None and splittag[0] in self.package:
            if len(splittag)==1:
                print self.package[splittag[0]].show(None)
            else:
                self.package[splittag[0]].show(splittag[1])
        else:
            for pkg in self.package:
                self.package[pkg].show(tag)
            
        
    class Package:
        def __init__(self, name="", licenses=[], aliases={},tags=[], descriptions={}):
            self.name=name
            self.licenses=licenses
            self.aliases=aliases
            self.tags=tags
            self.descriptions=descriptions

        def update(self, tag, value):
            attribute=None
            if ':' in tag:
                tag,attribute=tag.split(':',1)
            if tag=='license':
                self.licenses.append(value)
            if tag=='alias':
                self.aliases[attribute]=value
            if tag=='tag':
                if value not in self.tags:
                    self.tags.append(value)
            if tag=='summary' or tag=='description':
                if not attribute:
                    attribute='en'
                if attribute in self.descriptions:
                    self.descriptions[attribute][tag]=value
                else:
                    self.descriptions[attribute]={tag:value}
        
        def remove(self, tag, value=None):
            attribute=None
            if ':' in tag:
                tag,attribute=tag.split(':',1)
            if tag=='license':
                if value is not None:
                    self.licenses.remove(value)
                else:
                    self.licenses =[]
            if tag=='alias':
                if attribute is not None:
                    del self.aliases[attribute]
                else:
                    self.aliases={}
            if tag=='tag':
                if value is not None:
                    if value in self.tags:
                        self.tags.remove(value)
                self.tags=[]
            if tag=='summary' or tag=='description':
                if not attribute:
                    attribute='en'
                if attribute in self.descriptions:
                    del self.descriptions[attribute][tag]
                if len(self.descriptions[attribute])==0:
                    del self.descriptions[attribute]
    
        def show(self,tag):
            attribute=None
            if tag is not None and ':' in tag:
                tag,attribute=tag.split(':',1)
            if tag=='name' or tag==None:
                print self.name+'Name',self.name
            if tag=='license' or tag==None:
                print self.name+'Licenses',self.licenses
            if tag=='alias' or tag==None:
                print self.name+'Aliases',self.aliases
            if tag=='tag' or tag==None:
                print self.name+'Tags',self.tags
            if tag=='summary' or tag==None:
                for lang in self.descriptions:
                    print self.name+lang.capitalize()+'Summary',self.descriptions[lang]['summary']
            if tag=='description' or tag==None:
                for lang in self.descriptions:
                    print self.name+lang.capitalize()+'Description',self.descriptions[lang]['description']
