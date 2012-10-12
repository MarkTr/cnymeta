#! /usr/bin/python
import sys
import argparse
import xml.etree.ElementTree as et

def defineArgs(meta):
    parser = argparse.ArgumentParser('Create and modify metafiles')
    subparsers = parser.add_subparsers(description="add remove delete show change")
    addparser = subparsers.add_parser("add", help="Add new meta information")
    rmparser = subparsers.add_parser("rm", help="Remove meta information")
    delparser = subparsers.add_parser("del", help="delete all meta information")
    showparser = subparsers.add_parser("show", help="Show meta information")
    changeparser = subparsers.add_parser("change", help="Change meta information")
    
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
    parser.add_argument("-n", action="store_true", default=False, help="Create new metafile")
    parser.add_argument("-d", action="store", dest="dir", help="create template here instead of pwd")
    parser.add_argument("-f", action="store_true", default=False, help="Overwrite existing files")

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

class Metaparser:   
    
    def __init__(self, sauce):
        self.tree = et.parse(sauce)
        self.root = self.tree.getroot()
            
    def addMeta(self, path="/", tag="", attribute=None, text=""):
        if tag:
            parent = self.root.find(path)
            e = et.SubElement(parent,tag)
            if attribute:
                e.attrib = attribute
            if text:
                e.text = text
        self.write("addtest.sauce")
            
    def rmMeta(self, path="/", tag="", attribute=None, text=""):
        for p in self.root.findall(path):
            for e in p.getchildren():
                if not tag == e.tag and not text or text == e.text and not attribute or attribute == e.attrib:
                   p.remove(e)
                   self.write("rmtest.sauce")
    
    def changeMeta(self, path="/", tag="", attribute=None, text=None):
        for l in root.findall("source/licensing/license"):
            if l.text == "LGPLv2+":
                l.text = "LGPLv2.1+"
        self.write("changetest.sauce")
        
    def showMeta(self, path=""):
        if not True:
            et.dump(self.root)
            return
        for e in self.root.findall(path):
            et.dump(e)
    
    def addCmd(self, args):
        attribute = self.splitAttribute(args.attribute)
        self.addMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text)
    
    def rmCmd(self, args):
        attribute = self.splitAttribute(args.attribute)
        self.rmMeta(path=args.path, tag=args.tag, attribute=attribute, text=args.text)
        
    def delCmd(self, args):
        pass
    
    def showCmd(self, args):
        print args.path
        self.showMeta(path=args.path)
        
    def changeCmd(self, args):
        pass

    def splitAttribute(self, attributeStr):
        if not attributeStr:
            return None
        tmpattr = attributeStr.split('=')
        return {tmpattr[0]:tmpattr[1]}
        
    def write(self, filename):
        if sys.version_info<(2,7):
            self.tree.write(filename, encoding="UTF-8")
        else:
            self.tree.write(filename, encoding="utf-8", xml_declaration=True)
        
def main():
    meta = Metaparser("foo.sauce")
    defineArgs(meta)

if __name__ == "__main__":
    main()
    
