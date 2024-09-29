#!/usr/bin/env python3

import gzip
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.sax
from datetime import datetime, timezone
from xml.sax.handler import ContentHandler
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Merge extracted logo files into a LogoSearch index.')
    parser.add_argument('--gzip', action='store', default=True, help='compress output with gzip')
    parser.add_argument('--language', action='store', default='en', help='which Wikipedia language we are processing')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='output file')
    parser.add_argument('files', nargs='+', help='list of files to process')
    return parser.parse_args()



def main():
    global startTime
    startTime = datetime.now(timezone.utc)

    args = parse_args()

    images = []
    for file in args.files:
        sys.stderr.write(f'INFO: Processing {file}...\n')
        fin = open(file)
        images += json.load(fin)
        fin.close()

    sys.stderr.write(f'INFO: Writing to {args.output.name} (compression={args.gzip})...\n')
    #fout = gzip.compress(args.output) if args.gzip else args.output
    fout = args.output

    json.dump({
        'handle': f'wikipedia-{args.language}-infobox',
        'images': images,
        'lastmodified': datetime.now(timezone.utc).isoformat(),
        'logo': 'https://www.vectorlogo.zone/logos/wikipedia/wikipedia-icon.svg',
        'name': f'Wikipedia {args.language} Infobox Logos',
        'provider': 'remote',
        'provider_icon': 'https://logosear.ch/images/remote.svg',
        'url': f'https://{args.language}.wikipedia.org/wiki/Main_Page',
        'website': f'https://{args.language}.wikipedia.org/wiki/Main_Page'
    }, fout, indent=2)


    now = datetime.now(timezone.utc)
    delta = now - startTime
    sys.stderr.write(f'INFO: complete! elapsed time={delta}\n')

if __name__ == '__main__':
    main()
