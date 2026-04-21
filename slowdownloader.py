#!/bin/env python3

# slowdownloader.py - download files with long timeout

import argparse
import os
import pycurl
import sys
import yaml

DEBUG=False

def getargs():
    '''parse CL args'''
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--urlfile",  help="YAML URL file")
    parser.add_argument("-t", "--timeout", help="timeout (secs)",
						type=int, default=300)
    parser.add_argument("--ipv4", action="store_true", help="force IPv4")
    args = parser.parse_args()
    return args

def die(errmsg):
    print(errmsg, file=sys.stderr)
    sys.exit(1)


def downloadfile(url, filename, timeout, ipv4):
    with open(filename, 'wb') as f:
        c = pycurl.Curl()
        if ipv4:
            c.setopt(c.IPRESOLVE, c.IPRESOLVE_V4)
        c.setopt(c.URL, url)
        c.setopt(c.USERAGENT, 'curl/7.45.0')
        c.setopt(c.TIMEOUT, timeout)
        c.setopt(c.WRITEDATA, f)
        c.perform()
        c.close()

def downloader(urls, default_timeout, ipv4):
    for dl in urls:
        thisdl = urls[dl]
        url = thisdl['url']
        if DEBUG:
            print('DEBUG: URL %s' % url)
        # get filename from URL if not supplied
        urlfile = thisdl.get('filename', url.split('/')[-1])
        downloadfile(url, urlfile, default_timeout, ipv4)


def loadurls(urlfile):
    try:
        with open(urlfile, 'r') as yamlfile:
            urls = yaml.safe_load(yamlfile)
    except FileNotFoundError:
        die('%s no found' % urlfile)
    return urls


def main():
    global DEBUG
    if os.getenv('SLDEBUG'):
        print('DEBUG active')
        DEBUG = True
    args = getargs()
    urls = loadurls(args.urlfile)
    downloader(urls, args.timeout, args.ipv4)


if __name__ == '__main__':
    main()
