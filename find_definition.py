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

class ViewInvocation(AbstractInvocation):
   ''' view FILENAME -c PATTERN - give it control '''
   def __init__(self):
      self.CMD='view'
      self.waitFor=True
   def invoke(self, filename, expattern):
      args = [self.CMD, filename, '-c', expattern,
            '-c', 'redraw',
            '-c', 'set nohlsearch']
      # -c redraw => avoids that pesky "Press Enter to continue"
      # -c set nohlsearch => don't highlight the line, just put the cursor there
      proc = subprocess.Popen(args, executable=self.CMD)
      # let it inherit from parent
      if self.waitFor:
         proc.wait()
         if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode)

class GViewInvocation(ViewInvocation):
   ''' gview FILENAME -c PATTERN - launch it and leave it '''
   def __init__(self):
      self.CMD='gview'
      self.waitFor=False

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
      gen = TagsSearcherFactory().get_generator(config.get(CONFIG_SECTION, KEY_TAGS)).generate(args.string_to_search_for)
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

   tag = TagsSearcherFactory().get(config.get(CONFIG_SECTION, KEY_TAGS)).find(args.string_to_search_for)
   if tag is None:
      print "Not found, sorry"
      sys.exit(1)
   else:
      invocation.invoke(tag.filename, tag.pattern)

