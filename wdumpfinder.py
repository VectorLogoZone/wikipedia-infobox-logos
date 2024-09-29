#!/usr/bin/env python3

import argparse
import re
import requests
import sys
from bs4 import BeautifulSoup

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Find Wikipedia dump download links')
parser.add_argument('--date', type=str, default='latest', help='The date of the dump in YYYYMMDD format or "latest"')
#LATER: add support for other languages

def main():
    args = parser.parse_args()

    # Fetch the HTML content
    url = f'https://dumps.wikimedia.org/enwiki/{args.date}/'
    sys.stderr.write(f'INFO: fetching {url}...\n')
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        sys.stderr.write(f'ERROR: failed to fetch {url}: {response.status_code}\n')
        sys.exit(1)

    html_content = response.content
    sys.stderr.write(f'INFO: fetched {len(html_content)} bytes\n')

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all links
    links = soup.find_all('a', href=True)
    sys.stderr.write(f'INFO: found {len(links)} total links\n')

    # filter to just ones named "pages-articlesN.xml-pNpN.bz2"
    links = [link for link in links if re.search(r'pages-articles-multistream\d+.xml-p\d+p\d+.bz2$', link['href'])]
    sys.stderr.write(f'INFO: found {len(links)} matching links\n')

    # sort array numerically
    links = sorted(links, key=lambda link: int(re.search(r'p(\d+)p\d+', link['href']).group(1)))

    # Print the extracted links
    for link in links:
        print(f'{url}{link["href"]}')

if __name__ == '__main__':
    main()
