#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import argparse
import lxml.etree as et
import os #Metatemplate
import metadata as md

class Spoon:
    def __init__(self):
        self.tree = None
        self.root = None
        path = os.getcwd().rstrip('/') 
        name = os.path.basename(path)
        sauce = path +'/' + name + ".sauce"
        self.sauce=sauce
        self.meta=None
        #self._initSauce()
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
        subparsers = parser.add_subparsers(dest="scope", description="update/rm/new/reset/config/check")
        configparser = subparsers.add_parser("config", help="print config")
        checkparser = subparsers.add_parser("check", help="check meta information")
        newparser = subparsers.add_parser("new", help="create new metadata template")
        resetparser = subparsers.add_parser("reset", help="reset metadata template")
        globalshowparser = subparsers.add_parser("show", help="show all metadata")
        newparser.add_argument("recipeType", action="store", nargs='?', 
            choices=['default', 'superclass', 'factory', 'info', 'redirect'], default='default')
        resetparser.add_argument("recipeType", action="store", nargs='?', 
            choices=['default', 'superclass', 'factory', 'info', 'redirect'], default='default')
        
        commonparser = argparse.ArgumentParser(add_help=False)
        commonsubparsers = commonparser.add_subparsers(dest='command')
        commonargument = argparse.ArgumentParser(add_help=False)
        commonargument.add_argument("argument", action="store",nargs='+',
            help="tag to add/remove/show")
        
        updateparser = commonsubparsers.add_parser("update", parents=[commonargument], help="add/update meta information")
        rmparser = commonsubparsers.add_parser("rm", parents=[commonargument], help="remove meta information")
        showparser = commonsubparsers.add_parser("show", help="show meta information")
        showparser.add_argument("argument", action="store", nargs='?', default=None)
        sourceparser = subparsers.add_parser("source", parents=[commonparser], help="modify source component")
        pkgparser = subparsers.add_parser("package", parents=[commonparser], help="modify packages component")
        flavorparser = subparsers.add_parser("flavor", parents=[commonparser], help="modify flavor component")
        targetparser = subparsers.add_parser("target", parents=[commonparser], help="modify target component")
        typeparser = subparsers.add_parser("type", help="set the type of the recipe")
        typeparser.add_argument("recipeType", action="store", choices=['default', 'superclass', 'factory', 'info', 'redirect'])
        configparser.set_defaults(func=self._configCmd)
        checkparser.set_defaults(func=self._checkCmd)
        newparser.set_defaults(func=self._newCmd)
        resetparser.set_defaults(func=self._resetCmd)
        sourceparser.set_defaults(func=self._scopeCmd)
        pkgparser.set_defaults(func=self._scopeCmd)
        flavorparser.set_defaults(func=self._scopeCmd)
        targetparser.set_defaults(func=self._scopeCmd)
        typeparser.set_defaults(func=self._typeCmd)
        globalshowparser.set_defaults(func=self._showCmd)
        
        for arg in newargs:
            args=parser.parse_args(arg)
            args.func(args)
        self.meta.write()
        
    
    def _initSauce(self,args,createTemplate=False):
        if self.meta is None:
            if createTemplate:
                self.meta = md.MetaData(sauce=self.sauce,createTemplate=createTemplate,recipeType=args.recipeType)
            else:
                self.meta = md.MetaData(sauce=self.sauce,createTemplate=createTemplate)
            #self.root = self.tree.getroot()

    def showMeta(self, scope=None,tag=None):
        self.meta.show(scope=scope,tag=tag)

    def _scopeCmd(self, args):
        self._initSauce(args)
        if args.command=='show':
            self.showMeta(scope=args.scope,tag=args.argument)
            return
        for tag in args.argument:
            data=tag.split('=')
            if args.command=='update':
                self.meta.update(args.scope, data[0],data[1] if len(data)>1 else None)
            if args.command=='rm':
                self.meta.remove(args.scope, data[0],data[1] if len(data)>1 else None)


    def _showCmd(self,args):
        self._initSauce(args)
        self.showMeta()
        
    def _typeCmd(self,args):
        self._initSauce(args)
        # misusing scope on purpose here
        self.meta.update('recipe', args.scope, args.recipeType)
        self.showMeta()
        
    def _configCmd(self, args):
        pass

    def _resetCmd(self, args):
        self._newCmd(args,force=True)

    def _checkCmd(self, args):
        self._initSauce(args)
        self.showMeta()

    def _newCmd(self, args, force=False):
        if os.path.isfile(self.sauce) and not force:
            exit("soucefile already exists")
        self._initSauce(args,createTemplate=True)
        self.meta.write()

    def write(self):
        self.tree.write(self.sauce, encoding="utf-8", pretty_print=True, xml_declaration=True)

def main():
    spoon = Spoon()

if __name__ == "__main__":
    main()

