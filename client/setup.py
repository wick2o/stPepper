#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import os
import sys

def main():
	setup(console = [{'script': 'client.py', 'icon_resources' : [(1, 'yellowsub.ico')]}],
		options = {'py2exe': {'bundle_files' : 1, 'includes' : ['poster'], 'dll_excludes': ['w9xpopen.exe'],}},
		zipfile = None,
		optimize = 2,
		icon_resources = [(1, 'yellowsub.ico')],
		)
		
def cleanup():
	if os.name != 'posix':
		os.system("rmdir /S /Q build")
		os.system("move /y dist\client.exe .")
		os.system("rmdir /S /Q dist")
	else:
		os.system("rm -rf build")

	
if __name__ == "__main__":
	main()
	cleanup()