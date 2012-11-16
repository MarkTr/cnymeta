#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import argparse
import lxml.etree as et
import os #Metatemplate
import metadata as md

class Spoon:
    def __init__(self):
        self.sauce = None
        self.tree = None
        self.root = None
        self._defineArgs()

    def __checkKeyword(self,word):
        return (word=='source' or word=='package' or word=='flavor' or word=='new'
                or word=='target' or word=='config' or word=='check')
                
    def _defineArgs(self):
        tmpparser = argparse.ArgumentParser(add_help=False)
        tmpparser.add_argument("argument", action="store",nargs='+', help="tag to add/remove/show")
        tmparg=['--']
        tmparg.extend(sys.argv[1:])
        args = tmpparser.parse_args(tmparg)
        newargs=[]
        sublist=None
        for arg in args.argument:
            if self.__checkKeyword(arg):
                if sublist is not None:
                    newargs.append(sublist)
                sublist=[]
            if sublist is not None:
                sublist.append(arg)
        newargs.append(sublist)

        parser = argparse.ArgumentParser('Create and modify metafiles')
        subparsers = parser.add_subparsers(description="update/rm/new/reset/config/check")
        configparser = subparsers.add_parser("config", help="print config")
        checkparser = subparsers.add_parser("check", help="check meta information")
        newparser = subparsers.add_parser("new", help="create new metadata template")
        resetparser = subparsers.add_parser("reset", help="reset metadata template")
        
        commonparser = argparse.ArgumentParser(add_help=False)
        commonsubparsers = commonparser.add_subparsers(dest='action')
        commonargument = argparse.ArgumentParser(add_help=False)
        commonargument.add_argument("argument", action="store",nargs='+',
            choices=['homepage','license','tag','alias','name','summary','description','flavor', 'target'],
            help="tag to add/remove/show")
        
        updateparser = commonsubparsers.add_parser("update", parents=[commonargument], help="add/update meta information")
        rmparser = commonsubparsers.add_parser("rm", parents=[commonargument], help="remove meta information")
        sourceparser = subparsers.add_parser("source", parents=[commonparser], help="modify source component")
        pkgparser = subparsers.add_parser("package", parents=[commonparser], help="modify packages component")
        flavorparser = subparsers.add_parser("flavor", parents=[commonparser], help="modify flavor component")
        targetparser = subparsers.add_parser("target", parents=[commonparser], help="modify target component")
        typeparser = subparsers.add_parser("type", help="set the type of the recipe")
        typeparser.add_argument("recipeType", action="store", choices=['default', 'superclass', 'factory', 'info', 'redirect'])
        configparser.set_defaults(func=self._sourceCmd)
        checkparser.set_defaults(func=self._sourceCmd)
        newparser.set_defaults(func=self._sourceCmd)
        resetparser.set_defaults(func=self._sourceCmd)
        sourceparser.set_defaults(func=self._sourceCmd)
        pkgparser.set_defaults(func=self._sourceCmd)
        flavorparser.set_defaults(func=self._sourceCmd)
        targetparser.set_defaults(func=self._sourceCmd)
        typeparser.set_defaults(func=self._sourceCmd)
        
        for arg in newargs:
            args=parser.parse_args(arg)
            args.func(args)
        
        #subparsers = parser.add_subparsers(description="add remove delete show change")
        #addparser = subparsers.add_parser("add", help="Add new meta information")
        #rmparser = subparsers.add_parser("rm", help="Remove meta information")
        #delparser = subparsers.add_parser("del", help="delete all meta information")
        #showparser = subparsers.add_parser("show", help="Show meta information")
        #changeparser = subparsers.add_parser("change", help="Change meta information")
        #newparser = subparsers.add_parser("new", help="Create a new Template")
    
        #newparser.set_defaults(func=self.newCmd)
        #addparser.set_defaults(func=self.addCmd)
        #rmparser.set_defaults(func=self.rmCmd)
        #delparser.set_defaults(func=self.delCmd)
        #showparser.set_defaults(func=self.showCmd)
        #changeparser.set_defaults(func=self.changeCmd)
    
        #for p in [addparser,changeparser,rmparser,showparser]:
            #p.add_argument("-p", action="store", dest="path", default="", required=True, help="path inside sauce")
            #if p!=showparser:
                #p.add_argument("-t", action="store", dest="tag", required=True, help="tag to add/remove/show")
                #p.add_argument("-x", action="store", dest="text", help="text to add/remove/show")
                #p.add_argument("-a", action="store", dest="attribute", help="attribute to add/remove/show")
            #p.add_argument("-d", action="store", dest="dir", default=None, help="create template here instead of pwd")
        #changeparser.add_argument("-ox", action="store", dest="oldtext", help="text to replace")
        #changeparser.add_argument("-oa", action="store", dest="oldattr", help="attribute to replace")
        #rmparser.add_argument("-f", action="store_true", dest="force", default=False, help="Delete all matching tags")
        #newparser.add_argument("-t", action="store", dest="recipeType", default="default", help="Type of recipe <default|superclass|factory|info|redirect>")
        #newparser.add_argument("-f", action="store_true", dest="force", default=False, help="Overwrite existing files")
        #newparser.add_argument("-d", action="store", dest="dir", default=None, help="create template here instead of pwd")
    
        #args = parser.parse_args()
        #args.func(args)
    
    def initSauce(self,args):
        if not self.sauce or not self.tree or not self.root:
            self.path = args.dir if args.dir else os.getcwd() 
            self.path = self.path.rstrip('/')
            self.name = os.path.basename(self.path)
            self.sauce = self.path +'/' + self.name + ".sauce"
            if os.path.isfile(self.sauce):
                self.tree = et.parse(self.sauce)
                self.root = self.tree.getroot()

    def populateSource(self):
        self.addMeta("", tag="source")
        self.addMeta("source", tag="homepage", text="http://www.foresightlinux.org")
        self.addMeta("source", tag="licensing")
        self.addMeta("source", tag="tags")
        self.addMeta("source", tag="aliases")

    def populateFlavors(self):
        self.addMeta("", tag="flavors")

    def populateTargets(self):
        self.addMeta("", tag="targets")
        self.addMeta("targets", tag="target", text="True", attribute={"arch":"x86"})
        self.addMeta("targets", tag="target", text="True", attribute={"arch":"x86_64"})

    def populatePackages(self):
        if self.recipeType != "factory" and \
           self.recipeType != "superclass":
            self.addMeta("", tag="packages")

    def createTemplate(self, recipeType):
        self.recipeType=recipeType
        ### later for recipe parsing
        #hasRecipe = os.path.isfile(path +'/' + name + '.recipe')
        #hasStateFile = os.path.isfile(path +'/' + 'CONARY')
        #print hasRecipe, hasStateFile

        self.tree = et.ElementTree(et.XML("<recipe></recipe>"))
        self.root = self.tree.getroot()
        self.root.set('type', recipeType)
        self.populateSource()
        self.populateFlavors()
        self.populateTargets()
        self.populatePackages()
        self.write()

    def addMeta(self, path="", tag="", attribute=None, text=""):
        if tag:
            parent = self.root if path=="" else self.root.find(path)
            e = et.SubElement(parent,tag)
            if attribute:
                e.attrib.update(attribute)
            if text:
                e.text = text
        self.write()

    def rmMeta(self, path="", tag="", attribute=None, text="", force=False):
        for p in self.root.findall(path):
            for e in p.getchildren():
                if tag == e.tag and (text=="" or text == e.text) and (not attribute or e.attrib and attribute == e.attrib) \
                   or tag == e.tag and force:
                    p.remove(e)
                    self.write()

    def changeMeta(self, path="", tag="", oldattribute=None, attribute=None, oldtext=None, text=None):
        if path=="" and tag=="" or tag=='recipe':
            if attribute and oldattribute==self.root.attrib:
                self.root.attrib.clear()
                self.root.attrib.update(attribute)
                self.write()
            return
        for p in self.root.findall(path):
            for e in p.getchildren():
                if tag == e.tag:
                     if text and oldtext == e.text:
                         e.text=text
                     if attribute and oldattribute == e.attrib:
                         e.attrib.clear()
                         e.attrib.update(attribute)
        self.write()

    def showMeta(self, path=""):
        if path=="":
            et.dump(self.root)
            return
        for e in self.root.findall(path):
            et.dump(e)

    def _sourceCmd(self, args):
        if args.action=='update':
            print 'update', args.argument
        else:
            print 'rm', args.argument
        #self.initSauce(args)
        #attribute = self.splitAttribute(args.attribute)
        #self.addMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text)

    def rmCmd(self, args):
        self.initSauce(args)
        attribute = self.splitAttribute(args.attribute)
        self.rmMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text, force=args.force)

    def delCmd(self, args):
        self.initSauce(args)
        self.createTemplate()

    def showCmd(self, args):
        self.initSauce(args)
        self.showMeta(path=args.path)

    def changeCmd(self, args):
        self.initSauce(args)
        attribute = self.splitAttribute(args.attribute)
        oldattr = self.splitAttribute(args.oldattr)
        self.changeMeta(path=args.path, tag=args.tag,
                        oldattribute=oldattr, attribute=attribute,
                        oldtext=args.oldtext, text=args.text)

    def newCmd(self, args):
        self.initSauce(args)
        if os.path.isfile(self.sauce) and not args.force:
            exit("soucefile already exists")
        if not args.recipeType:
            args.recipeType="default"
        self.createTemplate(args.recipeType)

    def splitAttribute(self, attributeStr):
        if not attributeStr:
            return None
        tmpattr = attributeStr.split('=')
        return {tmpattr[0]:tmpattr[1]}

    def write(self):
        self.tree.write(self.sauce, encoding="utf-8", pretty_print=True, xml_declaration=True)

def main():
    spoon = Spoon()

if __name__ == "__main__":
    main()

