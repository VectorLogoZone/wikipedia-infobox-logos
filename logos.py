#!/usr/bin/env python3

import bz2
import urllib.parse
import urllib.request
import xml.sax
from xml.sax.handler import ContentHandler

# See https://github.com/5j9/wikitextparser
import wikitextparser as wtp

url = 'http://localhost/enwiki-latest-pages-articles-multistream.xml.bz2'

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
    parsed = wtp.parse(text)
    for template in parsed.templates:
      if not template.name.startswith('Infobox'):
        continue
      for argument in template.arguments:
        if argument.name != 'logo':
          continue
        value = str(argument.value).strip()
        if not value:
          continue
        print('###################################################################')
        print(titleToUrl(base, title))
        print(str(template.name).strip())
        print(value)
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
allowed = frozenset(b'\'(),-.0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
def titleToUrl(base, title):
  chars = [];
  for b in title.encode():
    if b in allowed:
      chars.append(chr(b))
    elif b == ord(' '):
      chars.append('_')
    else:
      chars.append("%%%0.2X" % b)
  return urllib.parse.urljoin(base, ''.join(chars))

def main(url):
  markupParser = MarkupHandler()
  xmlParser = TextHandler(lambda base, title, text : markupParser.process(base, title, text))
  with urllib.request.urlopen(url) as byteStream:
    decompress(byteStream, lambda data : xmlParser.feed(data))

main(url)
