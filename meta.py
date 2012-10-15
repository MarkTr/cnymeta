#! /usr/bin/python
import sys
import argparse
import xml.etree.ElementTree as et
import os #Metatemplate
from xml.dom.minidom import parseString # no prettyprinting in etree

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
        p.add_argument("-d", action="store", dest="dir", help="create template here instead of pwd")
    changeparser.add_argument("-ox", action="store", dest="oldtext", help="text to replace")
    changeparser.add_argument("-oa", action="store", dest="oldattr", help="attribute to replace")
    newparser.add_argument("-n", action="store_true", default=False, help="Create new metafile")
    newparser.add_argument("-t", action="store", dest="recipeType", default="default", help="Type of recipe <default|superclass|factory|info|redirect>")
    newparser.add_argument("-f", action="store_true", default=False, help="Overwrite existing files")
    newparser.add_argument("-d", action="store", dest="dir", help="create template here instead of pwd")

    args = parser.parse_args()
    args.func(args)

# Maybe we need something like this to preserve Comments and doctype definition
class PIParser(et.XMLTreeBuilder):

   def __init__(self):
       et.XMLTreeBuilder.__init__(self)
       # assumes ElementTree 1.2.X
       self._parser.CommentHandler = self.handle_comment
       self._parser.ProcessingInstructionHandler = self.handle_pi
       self._target.start("document", {})

   def close(self):
       self._target.end("document")
       return et.XMLTreeBuilder.close(self)

   def handle_comment(self, data):
       self._target.start(et.Comment, {})
       self._target.data(data)
       self._target.end(et.Comment)

   def handle_pi(self, target, data):
       self._target.start(et.PI, {})
       self._target.data(target + " " + data)
       self._target.end(et.PI)

class MetaParser:
    def __init__(self, sauce):
        self.tree = et.parse(sauce)
        self.root = self.tree.getroot()

    def populateSource(self):
        homepage="http://www.foresightlinux.org"
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

    def createTemplate(self, path, recipeType):
        self.path = path.rstrip('/')
        self.name = os.path.basename(path)
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
        self.write("createtest.sauce")

    def addMeta(self, path="", tag="", attribute=None, text=""):
        if tag:
            parent = self.root.find(path)
            e = et.SubElement(parent,tag)
            if attribute:
                e.attrib = attribute
            if text:
                e.text = text
        #self.write("addtest.sauce")

    def rmMeta(self, path="", tag="", attribute=None, text=""):
        for p in self.root.findall(path):
            for e in p.getchildren():
                if tag == e.tag and not text or text == e.text and not attribute or attribute == e.attrib:
                   p.remove(e)
                   self.write("rmtest.sauce")

    def changeMeta(self, path="", tag="", oldattribute=None, attribute=None, oldtext=None, text=None):
        for p in self.root.findall(path):
            for e in p.getchildren():
                if tag == e.tag:
                     if text and oldtext == e.text:
                         e.text=text
                     if attribute and oldattribute == e.attrib:
                         e.attrib=attribute
        self.write("changetest.sauce")

    def showMeta(self, path=""):
        for e in self.root.findall(path):
            et.dump(e)

    def addCmd(self, args):
        attribute = self.splitAttribute(args.attribute)
        self.addMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text)

    def rmCmd(self, args):
        attribute = self.splitAttribute(args.attribute)
        self.rmMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text)

    def delCmd(self, args):
        self.createTemplate()

    def showCmd(self, args):
        self.showMeta(path=args.path)

    def changeCmd(self, args):
        attribute = self.splitAttribute(args.attribute)
        oldattr = self.splitAttribute(args.oldattr)
        self.changeMeta(path=args.path, tag=args.tag, 
                        oldattribute=oldattr, attribute=attribute, 
                        oldtext=args.oldtext, text=args.text)

    def newCmd(self, args):
        if not args.dir:
            args.dir=os.getcwd()
        if not args.recipeType:
            args.recipeType="default"
        self.createTemplate(args.dir, args.recipeType)

    def splitAttribute(self, attributeStr):
        if not attributeStr:
            return None
        tmpattr = attributeStr.split('=')
        return {tmpattr[0]:tmpattr[1]}

    def write(self, filename):
        sauce = open(filename, 'w')
        sauce.write(parseString(et.tostring(self.tree.getroot(),encoding="utf-8")).toprettyxml())
        sauce.close()
        #if sys.version_info<(2,7):
        #    self.tree.write(filename, encoding="UTF-8")
        #else:
        #    self.tree.write(filename, encoding="utf-8", xml_declaration=True)

def main():
    meta = MetaParser("foo.sauce")
    defineArgs(meta)

if __name__ == "__main__":
    main()

