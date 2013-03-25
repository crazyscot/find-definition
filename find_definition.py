#!/usr/bin/env python

import sys, os, subprocess, ConfigParser, argparse

from TagsSearch import *

CONFIG = os.path.expanduser('~/.find_definition')
CONFIG_SECTION = 'DEFAULT'
KEY_TAGS = 'tagsfile'
KEY_INVOCATION = 'invocation'

class AbstractInvocation:
   def invoke(self, filename, expattern):
      raise TypeError,'Abstract interface!'

class AbstractTagInvocation:
   def invokeTag(self, tag):
      raise TypeError,'Abstract interface!'

class ViewInvocation(AbstractInvocation, AbstractTagInvocation):
   ''' view FILENAME -c PATTERN - give it control '''
   def __init__(self):
      self.CMD='view'
      self.waitFor=True

   def invoke(self, filename, expattern):
      '''Old-style invocation, written before I realised "vim -t" existed'''
      args = [self.CMD, filename, '-c', expattern,
            '-c', 'redraw',
            '-c', 'set nohlsearch']
      # -c redraw => avoids that pesky "Press Enter to continue"
      # -c set nohlsearch => don't highlight the line, just put the cursor there
      self.run(args)

   def invokeTag(self, tag):
      '''New-style invocation, better than the old style as it puts the
         tag into the vim tags stack - so you can immediately use :tn if
         the first hit isn't the one you wanted '''
      args = [self.CMD, '-t', tag]
      self.run(args)

   def run(self, args):
      proc = subprocess.Popen(args, executable=self.CMD)
      # let it inherit from parent
      if self.waitFor:
         proc.wait()
         if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode)

class GViewInvocation(ViewInvocation):
   ''' gview FILENAME -t TAG - launch it and leave it '''
   def __init__(self):
      self.CMD='gview'
      self.waitFor=False

def getTagsFiles(config):
   return config.get(CONFIG_SECTION, KEY_TAGS).split(":")

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Find source code definitions.')
   parser.add_argument('--complete', action='store_true', help='Lists possible expansions for tab-completion')
   parser.add_argument('string_to_search_for')
   args = parser.parse_args()

   config = ConfigParser.SafeConfigParser({
      KEY_TAGS : os.path.expanduser('~/Work/Mainline/tags'),
      KEY_INVOCATION : 'ViewInvocation',
      })
   if os.path.exists(CONFIG):
      config.read(CONFIG)

   if args.complete:
      tagsfiles = getTagsFiles(config)
      for t in tagsfiles:
         gen = TagsSearcherFactory().get_generator(t).generate(args.string_to_search_for)
         for tag in gen:
            print tag.tag(),
      sys.exit(0)

   invokeme = config.get(CONFIG_SECTION, KEY_INVOCATION)
   if invokeme in globals().keys():
      invocation = globals()[invokeme]()
   else:
      # Not in scope, so we'll try the equivalent of:
      #     import CLASS
      #     invocation = CLASS()
      module = __import__(invokeme)
      try:
         invclass = getattr(module,invokeme) # raises if not found
      except AttributeError,e:
         raise AttributeError,('Source module %s does not contain a class %s? (from %s)'%(invokeme,invokeme, e.args))
      try:
         invocation = invclass()
      except TypeError,t:
         raise TypeError,('Class %s does not have a no-parameter constructor? (from %s)'%(invokeme, t.args))

   tagsfiles = getTagsFiles(config)

   if isinstance(invocation,AbstractTagInvocation):
      invocation.invokeTag(args.string_to_search_for)
   else:
      for t in tagsfiles:
         tag = TagsSearcherFactory().get(t).find(args.string_to_search_for)
         if tag is not None:
            invocation.invoke(tag.filename(), tag.pattern())
            sys.exit(0)
      print "Not found, sorry"
      sys.exit(1)
