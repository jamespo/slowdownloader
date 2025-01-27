#!/bin/env python3

# slowdownloader.py - download files with long timeout

import argparse
import pycurl
import sys
import yaml

def getargs():
    '''parse CL args'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--urlfile",  help="YAML URL file")
    parser.add_argument("-t", "--timeout", help="timeout (secs)",
						type=int, default=300)
    args = parser.parse_args()
    return args

def die(errmsg):
    print(errmsg, file=sys.stderr)
    sys.exit(1)


def downloadfile(url, filename):
    with open(filename, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, f)
        c.perform()
        c.close()

def downloader(urls):
    for dl in urls:
        thisdl = urls[dl]
        url = thisdl['url']
        # get filename from URL if not supplied
        urlfile = thisdl.get('filename', url.split('/')[-1])
        downloadfile(url, urlfile)


def loadurls(urlfile):
    try:
        with open(urlfile, 'r') as yamlfile:
            urls = yaml.safe_load(yamlfile)
    except FileNotFoundError:
        die('%s no found' % urlfile)
    return urls


def main():
    args = getargs()
    urls = loadurls(args.urlfile)
    downloader(urls)


if __name__ == '__main__':
    main()
