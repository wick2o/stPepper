#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import zipfile

try:
	import argparse
except ImportError:
	print "Missing needed module: easy_install argparse"
	sys.exit()


def setup():
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--outzip', action='store', dest='outzip', required=True, help='filename for zipfile')
	parser.add_argument('-f', '--folder', action='store', dest='folder', required=True, help='folder to zip up')
	global args
	args = parser.parse_args()	


def main():
	setup()
	zip = zipfile.ZipFile(args.outzip, 'w')
	for root,dirs, files in os.walk(args.folder):
		for file in files:
			zip.write(os.path.join(root, file))
	zip.close()
	
if __name__ == "__main__":
	main()