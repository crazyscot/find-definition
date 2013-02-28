#!/usr/bin/env python

import sys, os, subprocess, ConfigParser

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
      args = [self.CMD, filename, '-c', expattern, '-c', 'redraw']
      # -c redraw => avoids that pesky "Press Enter to continue"
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
   helpRequested = False
   if len(sys.argv) > 1 and sys.argv[1]=='--help':
      helpRequested = True
   if len(sys.argv) != 2 or helpRequested:
      print "Usage: %s TermToSearchFor"%sys.argv[0]
      if helpRequested: sys.exit(0)
      sys.exit(1)

   config = ConfigParser.SafeConfigParser({
      KEY_TAGS : os.path.expanduser('~/Work/Mainline/tags'),
      KEY_INVOCATION : 'ViewInvocation',
      })
   if os.path.exists(CONFIG):
      config.read(CONFIG)

   needle = sys.argv[1]

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

   tag = TagsSearcherFactory().get(config.get(CONFIG_SECTION, KEY_TAGS)).find(needle)
   if tag is None:
      print "Not found, sorry"
      sys.exit(1)
   else:
      invocation.invoke(tag.filename, tag.pattern)

