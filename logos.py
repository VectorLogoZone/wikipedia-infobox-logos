#!/usr/bin/env python3

import bz2
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.sax
from datetime import datetime, timezone
from xml.sax.handler import ContentHandler

# https://github.com/earwig/mwparserfromhell
import mwparserfromhell as mwp

logoBase = 'https://en.wikipedia.org/wiki/Special:Redirect/file'
url = 'http://localhost/enwiki-latest-pages-articles-multistream.xml.bz2'
tags = frozenset(['logo'])

articleCount = 0
infoCount = 0
startTime = None
svgLogoCount = 0

class JsonHandler():
  def __init__(self, file=sys.stdout):
    self.count = 0
    self.file = file

  def add(self, img, name, src):
    if self.count:
      print(',', file=self.file)
    else:
      text = self.buildJson()
      offset = text.find(']')
      print(text[:offset], file=self.file)
    print(json.dumps({'img': img, 'name': name, 'src': src }, separators=(',', ':')), end='', file=self.file)
    self.count = self.count + 1

  def buildJson(self):
    return json.dumps({
      'handle': '',
      'images': [],
      'lastmodified': isodatetime(),
      'logo': '',
      'name': '',
      'provider': '',
      'provider_icon': '',
      'url': '',
      'website': ''
    }, indent=0)

  def end(self):
    print('', file=self.file)
    text = self.buildJson()
    offset = text.find(']')
    print(text[offset:], file=self.file)

class MarkupHandler():
  def __init__(self, output):
    self.output = output

  def process(self, base, title, text):
    global articleCount, infoCount, svgLogoCount
    if articleCount % 1000 == 0:
      now = datetime.utcnow()
      delta = now - startTime
      print(isodatetime(now), delta.total_seconds(), articleCount, infoCount, svgLogoCount, file=sys.stderr)
    articleCount = articleCount + 1
    parsed = mwp.parse(text)
    hasInfobox = False
    for template in parsed.ifilter_templates():
      name = str(template.name).strip()
      if name[0:7].lower() != 'infobox':
        continue
      infoCount = infoCount + 1
      hasInfobox = True
      for argument in template.params:
        tag = str(argument.name).strip().lower()
        if not tag in tags:
          continue
        pageUrl = urllib.parse.urljoin(base, urlencode(title))
        logoUrls = imageValueToUrls(argument.value)
        for logoUrl in logoUrls:
          svgLogoCount = svgLogoCount + 1
          self.output.add(logoUrl, title, pageUrl)

class TextHandler(ContentHandler):
  def __init__(self, process):
    self._chunks = []
    self._parser = xml.sax.make_parser()
    self._parser.setContentHandler(self)
    self._process = process
    self._base = ''
    self._title = ''

  def characters(self, chunk):
    self._chunks.append(chunk)

  def endElement(self, name):
    text = ''.join(self._chunks)
    if name == 'text':
      self._process(self._base, self._title, text)
    elif name == 'base':
      self._base = text
    elif name == 'title':
      self._title = text

  def feed(self, data):
    self._parser.feed(data)

  def startElement(self, name, attrs):
    self._chunks = []

def decompress(byteStream, feed):
  bufsize = 128 * 1024
  decompressor = bz2.BZ2Decompressor()
  while True:
    compressed = byteStream.read(bufsize)
    if not compressed:
      break
    while True:
      decompressed = decompressor.decompress(compressed)
      feed(decompressed)
      if decompressor.eof:
        compressed = decompressor.unused_data
        decompressor = bz2.BZ2Decompressor()
      else:
        break

def isodatetime(when=None):
  if when:
    when = when.replace(tzinfo=timezone.utc)
  else:
    when = datetime.now(timezone.utc)
  return when.isoformat()

refile = re.compile(r'(?i)^ *\[\[ *file *:')
def imageValueToUrls(value):
  value = str(value).strip() if value else ''
  values = [urlencode(value)]
  if refile.match(value):
    parsed = mwp.parse(value)
    values = [urlencode(wikilink.title.strip()) for wikilink in parsed.ifilter_wikilinks()]
  return [f'{logoBase}/{v}' for v in values if v.endswith('.svg')]

# See https://www.mediawiki.org/wiki/Manual:Page_title#Encoding
allowed = frozenset(b'\'(),-.0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz')
def urlencode(value):
  chars = []
  for b in value.encode():
    if b in allowed:
      chars.append(chr(b))
    elif b == ord(' '):
      chars.append('_')
    else:
      chars.append("%%%0.2X" % b)
  return ''.join(chars)

def main(url):
  global startTime
  startTime = datetime.utcnow()
  output = JsonHandler()
  markupParser = MarkupHandler(output)
  xmlParser = TextHandler(lambda base, title, text : markupParser.process(base, title, text))
  with urllib.request.urlopen(url) as byteStream:
    decompress(byteStream, lambda data : xmlParser.feed(data))
  output.end()
  now = datetime.utcnow()
  delta = now - startTime
  print('articleCount', articleCount, file=sys.stderr)
  print('infoCount', infoCount, file=sys.stderr)
  print('svgLogoCount', svgLogoCount, file=sys.stderr)
  print('elapsed', delta, file=sys.stderr)

if __name__ == '__main__':
  main(url)
