#!/usr/bin/env python3

import bz2
import re
import sys
import urllib.parse
import urllib.request
import xml.sax
from xml.sax.handler import ContentHandler

# https://github.com/earwig/mwparserfromhell
import mwparserfromhell as mwp

lang = 'en'
logoBase = 'https://en.wikipedia.org/wiki/Special:Redirect/file'
url = 'http://localhost/enwiki-latest-pages-articles-multistream.xml.bz2'

articleCount = 0;
infoCount = 0;
svgLogoCount = 0;

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
    text = ''.join(self._chunks);
    if name == 'text':
      self._process(self._base, self._title, text)
    elif name == 'base':
      self._base = text
    elif name == 'title':
      self._title = text

  def feed(self, data):
    self._parser.feed(data)

  def startElement(self, name, attrs):
    self._chunks = [];

class MarkupHandler():
  def process(self, base, title, text):
    global articleCount, infoCount, svgLogoCount
    if articleCount % 1000 == 0:
      print(articleCount, infoCount, svgLogoCount, file=sys.stderr)
    articleCount = articleCount + 1;
    parsed = mwp.parse(text)
    hasInfobox = False
    for template in parsed.ifilter_templates():
      name = str(template.name).strip()
      if name[0:7].lower() != 'infobox':
        continue
      hasInfobox = True
      for argument in template.params:
        arg = str(argument.name).strip().lower()
        if arg != 'logo':
          continue
        infoCount = infoCount + 1;
        logoUrl = logoValueToUrl(argument.value, parsed)
        if not logoUrl:
          continue
        svgLogoCount = svgLogoCount + 1
        pageUrl = urllib.parse.urljoin(base, urlencode(title))
        print('###################################################################')
        print(pageUrl)
        print(name)
        print(logoUrl)
        print('-------------------------------------------------------------------')

def decompress(byteStream, feed):
  bufsize = 128 * 1024;
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

# See https://www.mediawiki.org/wiki/Manual:Page_title#Encoding
allowed = frozenset(b'\'(),-.0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz')
def urlencode(value):
  chars = [];
  for b in value.encode():
    if b in allowed:
      chars.append(chr(b))
    elif b == ord(' '):
      chars.append('_')
    else:
      chars.append("%%%0.2X" % b)
  return ''.join(chars)

refile = re.compile(r'^ *\[\[ *file *:')
def logoValueToUrl(value, parsed):
  value = str(value).strip() if value else None
  if not value:
    return None
  if refile.match(value):
    for wikilink in parsed.ifilter_wikilinks():
      if value == str(wikilink):
        value = wikilink.title[5:]
        break
  if not value.strip().endswith('.svg'):
    return None
  value = urlencode(value)
  return f'{logoBase}/{value}'

def main(url):
  markupParser = MarkupHandler()
  xmlParser = TextHandler(lambda base, title, text : markupParser.process(base, title, text))
  with urllib.request.urlopen(url) as byteStream:
    decompress(byteStream, lambda data : xmlParser.feed(data))
  print('articleCount', articleCount)
  print('infoCount', infoCount)
  print('svgLogoCount', svgLogoCount)

main(url)
