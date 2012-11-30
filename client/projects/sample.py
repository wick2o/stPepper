#!/usr/bin/env python
# -*- coding: utf-8 -*-


def setup():
	import re
	import sys
	import urllib
	import urlparse
	try:
		from BeautifulSoup import BeautifulSoup
	except:
		print "Missing needed module: easy_install argparse"
		sys.exit()
	
def main(args, url):
	setup()
	print url

	