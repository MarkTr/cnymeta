#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import argparse
import lxml.etree as et
#import xml.etree.ElementTree as et
import os #Metatemplate
#from xml.dom.minidom import parseString # no prettyprinting in etree

def defineArgs(meta):
    parser = argparse.ArgumentParser('Create and modify metafiles')
    subparsers = parser.add_subparsers(description="add remove delete show change")
    addparser = subparsers.add_parser("add", help="Add new meta information")
    rmparser = subparsers.add_parser("rm", help="Remove meta information")
    delparser = subparsers.add_parser("del", help="delete all meta information")
    showparser = subparsers.add_parser("show", help="Show meta information")
    changeparser = subparsers.add_parser("change", help="Change meta information")
    newparser = subparsers.add_parser("new", help="Create a new Template")

    newparser.set_defaults(func=meta.newCmd)
    addparser.set_defaults(func=meta.addCmd)
    rmparser.set_defaults(func=meta.rmCmd)
    delparser.set_defaults(func=meta.delCmd)
    showparser.set_defaults(func=meta.showCmd)
    changeparser.set_defaults(func=meta.changeCmd)

    for p in [addparser,changeparser,rmparser,showparser]:
        p.add_argument("-p", action="store", dest="path", default="", required=True, help="path inside sauce")
        p.add_argument("-t", action="store", dest="tag", required= p!=showparser, help="tag to add/remove/show")
        p.add_argument("-x", action="store", dest="text", help="text to add/remove/show")
        p.add_argument("-a", action="store", dest="attribute", help="attribute to add/remove/show")
        p.add_argument("-d", action="store", dest="dir", default=None, help="create template here instead of pwd")
    changeparser.add_argument("-ox", action="store", dest="oldtext", help="text to replace")
    changeparser.add_argument("-oa", action="store", dest="oldattr", help="attribute to replace")
    rmparser.add_argument("-f", action="store_true", dest="force", default=False, help="Delete all matching tags")
    newparser.add_argument("-n", action="store_true", default=False, help="Create new metafile")
    newparser.add_argument("-t", action="store", dest="recipeType", default="default", help="Type of recipe <default|superclass|factory|info|redirect>")
    newparser.add_argument("-f", action="store_true", dest="force", default=False, help="Overwrite existing files")
    newparser.add_argument("-d", action="store", dest="dir", default=None, help="create template here instead of pwd")

    args = parser.parse_args()
    args.func(args)

class MetaParser:
    def __init__(self):
        self.sauce = None
        self.tree = None
        self.root = None

    def initSauce(self,args):
        if not self.sauce or not self.tree or not self.root:
            self.path = args.dir if args.dir else os.getcwd() 
            self.path = self.path.rstrip('/')
            self.name = os.path.basename(self.path)
            self.sauce = self.path +'/' + self.name + ".sauce"
            print self.sauce
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
        for e in self.root.findall(path):
            et.dump(e)

    def addCmd(self, args):
        self.initSauce(args)
        attribute = self.splitAttribute(args.attribute)
        self.addMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text)

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
    meta = MetaParser()
    defineArgs(meta)

if __name__ == "__main__":
    main()

