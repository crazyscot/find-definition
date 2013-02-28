import re

class TagsResponse:
   def __init__(self, filename, pattern):
      self.filename = filename
      self.pattern = pattern
   def __str__(self):
      return '[filename=%s pattern=%s]' % (self.filename, self.pattern)

def quote_pattern(pat):
   pat = re.sub('~', '\~', pat)
   pat = re.sub('\*', '\*', pat)
   pat = re.sub('\[', '\\[', pat)
   return pat

class CTag:
   def __init__(self, line):
      # We don't use the comment part (vi comment, introduced by ") -
      # so strip it out
      parts = line.split('"', 1)
      # curveball: sometimes the ex-command contains a tab.
      self.fields = parts[0].split('\t', 2)
   def to_response(self):
      return TagsResponse(self.filename(), self.pattern())
   def tag(self):
      return self.fields[0]
   def filename(self):
      return self.fields[1]
   def pattern(self):
      return quote_pattern(self.fields[2])

class AbstractTagsSearcher:
   '''
   Tags searching, using an unspecified algorithm.
   '''
   def __init__(self, tagsfile):
      self.tagsfile = tagsfile

   def find(self, tag):
      '''
      Searches for a tag. Returns a TagsResponse, or None if not found.
      NOTE: Only returns the first match it finds.
      '''
      raise 'Abstract interface!'
   def generate(self, tag):
      '''
      Tag search generator, i.e. returns an iterator that contains all
      possible completions. Not quite the same as find().
      '''
      raise 'Abstract interface!'

class LinearTagsSearcher(AbstractTagsSearcher):
   ''' Crungey old lsearch. '''
   def find(self,tag):
      f = open(self.tagsfile, 'r')
      needle = tag + '\t'
      for line in f:
         if line.startswith(needle):
            return CTag(line).to_response()
      return None

   def generate(self,tag):
      f = open(self.tagsfile, 'r')
      needle = tag # Different from find() !
      for line in f:
         if line.startswith(needle):
            yield CTag(line)

class BinaryTagsSearcher(AbstractTagsSearcher):
   ''' bsearch is faster, particularly on large files '''
   def find(self,needle):
      f = open(self.tagsfile, 'r')
      f.seek(0,2)
      size = f.tell()

      TOP = 0
      BOTTOM = size
      while True:
         MID = (TOP+BOTTOM)/2
         #print "Top %d Mid %d Bottom %d"%(TOP,MID,BOTTOM)
         f.seek(MID,0)
         f.readline() # throw away the partial line
         MID = f.tell()
         if MID>=BOTTOM:
            # Endgame... naive binary search fails to take account of line lengths, so use TOP as a false pivot
            MID = TOP
            f.seek(TOP,0)
            f.readline()
            MID=f.tell()
         if MID>=BOTTOM:
            return None # No?
         line = f.readline()
         ctag = CTag(line)
         tag = ctag.tag()
         #print "..-> %s"%tag

         if tag == needle:
            return ctag.to_response() # Jackpot!
         elif tag < needle:
            TOP = f.tell()-1 # end of the rejected mid-record
            #print "<<<"
         else: # needle > tag
            BOTTOM = MID # beginning of the rejected mid-record
            #print ">>>"

         if TOP>=BOTTOM:
            return None # Simple termination

class TagsSearcherFactory:
   def get(self, tagsfile):
      return BinaryTagsSearcher(tagsfile)
   def get_generator(self,tagsfile):
      return LinearTagsSearcher(tagsfile)

