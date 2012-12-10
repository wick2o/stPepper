#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
	import argparse
except ImportError:
	print "Missing needed module: easy_install argparse"
	sys.exit()

try:
	import sqlite3
except ImportError:
	print 'Missing needed module: easy_install sqlite3'
	sys.exit()

def setup():
	parser = argparse.ArgumentParser()
	opt_group = parser.add_mutually_exclusive_group()
	opt_group.add_argument('-s', '--single', action='store', dest='sfile',  help='Add single file to database')
	opt_group.add_argument('-f', '--folder', action='store', dest='folder', help='Add all files inside a folder to database')

	
	parser.add_argument('-d', '--database', action='store', dest='database', required=True, help='database file')
	parser.add_argument('-p', '--project', action='store', dest='project', required=True, help='project')
	
	global args
	args = parser.parse_args()
	
def main():
	setup()
	if os.path.exists(args.database):
		db = sqlite3.connect(args.database)
		c = db.cursor()
		
		if args.sfile:
			if os.path.exists(args.sfile) and os.path.isdir(args.sfile) == False:
				print "Adding %s..." % (os.path.basename(args.sfile))
				c.execute("INSERT INTO tasks (task,status) values ('%s','open')" % (os.path.basename(args.sfile)))
			else:
				print "File not found..."


		if args.folder:
			if os.path.exists(args.folder) and os.path.isdir(args.folder) == True:
				for root, dirs, files in os.walk(args.folder):
					for f in files:
						print "Adding %s..." % (f)
						c.execute("INSERT INTO tasks (task, project, status) values ('%s', '%s', 'open')" % (f,args.project))
			else:
				print "folder doesnt exist..."
		
		db.commit()
		c.close()
		sys.exit()
	else:
		print "Database not found..."
		sys.exit()

if __name__ == "__main__":
	main()