#!/usr/bin/env python3

import argparse
import bz2
import json
import re
import sys
import urllib.parse
import urllib3
import xml.sax
from datetime import datetime, timezone, UTC
from xml.sax.handler import ContentHandler

# https://github.com/earwig/mwparserfromhell
import mwparserfromhell as mwp

logoBase = 'https://en.wikipedia.org/wiki/Special:Redirect/file'
tags = frozenset(['logo'])

def parse_args():
    parser = argparse.ArgumentParser(description='Extract infobox logos from Wikipedia dump.')
    parser.add_argument('--prefix', action='store', default='', help='prefix for log lines')
    parser.add_argument('url', nargs=1, help='URL of the Wikipedia dump file (can be file:// or https://)')
    return parser.parse_args()

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
        return json.dumps([], indent=0)

    def end(self):
        print('', file=self.file)
        text = self.buildJson()
        offset = text.find(']')
        print(text[offset:], file=self.file)

class MarkupHandler():
    def __init__(self, prefix, output):
        self.prefix = prefix
        self.output = output

    def process(self, base, title, text):
        global articleCount, infoCount, svgLogoCount
        if articleCount % 1000 == 0:
            now = datetime.now(timezone.utc)
            delta = now - startTime
            print(f'{self.prefix}{isodatetime(now)} delta={delta.total_seconds()} articles={articleCount} boxes={infoCount} logos={svgLogoCount}', file=sys.stderr)
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

def main():
    args = parse_args()
    url = args.url[0]

    global startTime
    startTime = datetime.now(timezone.utc)
    output = JsonHandler()
    markupParser = MarkupHandler(args.prefix, output)
    xmlParser = TextHandler(lambda base, title, text : markupParser.process(base, title, text))
    with urllib3.request("GET", url, retries=5, preload_content=False) as byteStream:
        decompress(byteStream, lambda data : xmlParser.feed(data))
        #xmlParser.feed(byteStream)
    output.end()
    now = datetime.now(timezone.utc)
    delta = now - startTime
    print(f'{args.prefix}articleCount: {articleCount}', file=sys.stderr)
    print(f'{args.prefix}infoCount: {infoCount}', file=sys.stderr)
    print(f'{args.prefix}svgLogoCount: {svgLogoCount}', file=sys.stderr)
    print(f'{args.prefix}elapsed: {delta}', file=sys.stderr)

if __name__ == '__main__':
    main()
