#!/usr/bin/env python3

import argparse
import humanize
import requests
import sys

parser = argparse.ArgumentParser(description="Check sizes of URLs from a file.")
parser.add_argument('file', type=str, help='Path to the file containing URLs')


def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]


def check_url_size(url):

    response = requests.head(url)
    if response.status_code == 200:
        return int(response.headers.get('content-length', 0))

    sys.stderr.write(f'ERROR: failed to fetch {url}: {response.status_code}\n')

    return 0

def main():
    args = parser.parse_args()
    urls = read_urls_from_file(args.file)
    sys.stderr.write(f'INFO: checking sizes of {len(urls)} URLs...\n')

    total = 0
    for url in urls:
        size = check_url_size(url)
        sys.stderr.write(f'INFO: {url}: {humanize.naturalsize(size)} ({size})\n')
        total += size
    sys.stderr.write(f'INFO: total size={humanize.naturalsize(total)} ({total})\n')

# Example usage
if __name__ == '__main__':
    main()
