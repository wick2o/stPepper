#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import Queue
import signal
import time
from threading import Thread, activeCount, Lock, current_thread
from subprocess import call
import urllib2
import urllib
import string
import socket


__author__ = 'Jaime Filson aka WiK'
__license__ = 'BSD (3-Clause)'
__version__ = '0'
__date__ = ''
__maintainer__ = 'WiK'
__email__ = 'wick2o@gmail.com'
__status__ = 'Beta'

ipaddresses = []
queue = Queue.Queue()
sigint = False
foundips = []

valid_chars = '.%s%s' % (string.ascii_letters, string.digits)


def logo():
	print "     _     ___                           "
	print " ___| |_  / _ \___ _ __  _ __   ___ _ __ "
	print "/ __| __|/ /_)/ _ \ '_ \| '_ \ / _ \ '__|"
	print "\__ \ |_/ ___/  __/ |_) | |_) |  __/ |   "
	print "|___/\__\/    \___| .__/| .__/ \___|_|   "
	print "                  |_|   |_|              "
	print ""
	print "             - with a little help from my friends -"
	print ""
	print "Author:  %s" % (__author__)
	print "Version: %s" % (__version__)
	print "Status:  %s" % (__status__)
	print ""

def request_task():
	global f_name
	global valid_chars
	
	res = urllib2.urlopen('http://%s/gettask' % (args.server))
	f_name = res.info()['Content-Disposition'].split('filename=')[1].replace('"','')
	t_name = ''.join(c for c in f_name if c in valid_chars)
	
	if f_name == t_name:
		#print 'everything is legit'
		f_content = res.read()
		f = open(f_name, 'wb')
		f.write(f_content)
		f.close()
	else:
		print 'Error: Filename from server does not match a legit filename'
		sys.exit()
	
	res.close()
	
	
def load_ipaddresses():
	global f_name
	
	ip_file = open(f_name,'r')
	ip_read = ip_file.readlines()
	ip_read = [item.rstrip() for item in ip_read]
	for ip in ip_read:
		if not ip.startswith('#'): #ignore comments
			ipaddresses.append(ip)
	ip_file.close()
	
	
def run_process(ip):
	#print 'Looking up %s' % (ip)
	url = 'http://%s' % (ip)
	socket.setdefaulttimeout(2)
	
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1')
	try:
		res = urllib2.urlopen(req)
		foundips.append(ip)
	except:
		res = 'error'
	
		
def upload_results():
	global fname
	print "Completed Task: %s" % (f_name)
	df = '%s.done' % (f_name)
	f = open(df, 'wb')
	f.write('\n'.join(foundips))
	f.close()
	
	#Post to server:
	#call(["curl", "-X", "POST", "-T", f_name, , "-F", "name=submit", "http://50.17.217.148/upload?data="
	#cleanup
	if os.path.exists(f_name):
		os.remove(f_name)
	#if os.path.exists(df):
		#os.remove(df)

	

def process_handler(ipaddresses):
	if args.threads > 1:
		threads = []
		for ip in ipaddresses:
			queue.put(ip)
		progress_lock = Lock()

		while not queue.empty() and not sigint:
			if args.threads >= activeCount() and not sigint:
				ip = queue.get()
				try:
					# setup thread to run process
					t = Thread(target=run_process,args=(ip,))
					t.daemon = True
					threads.append(t)
					t.start()
				finally:
					progress_lock.acquire()
					try:
						#run a progress bar here
						pass
					finally:
						progress_lock.release()
					queue.task_done()
		while activeCount() > 1:
			time.sleep(0.1)
		for thread in threads:
			thread.join()

		queue.join()
	else:
		for ip in ipaddresses:
			run_process(ip)
	return


def signal_handler(signal, frame):
	#handles ctrl+c events
	global sigint
	global f_name
	sigint = True
		
	print ' Ctrl+C detected... exiting...\n'
	
	# cleanup from canceled task
	if os.path.exists(f_name):
		os.remove(f_name)
	
	sys.exit(1)

def setup():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--threads', action='store', dest='threads', default=0, type=int, help='Enable threading. Specifiy max # of threads')
	parser.add_argument('-m', '--maxtasks', action='store', dest='tasks', default=1, type=int, help='Max tasks to complete in a row')
	parser.add_argument('-w', '--wait', action='store', dest='wait', default=0, type=int, help='Wait time between tasks in seconds')
	parser.add_argument('-s', '--server', action='store',dest='server', required=True, help='IP address of the server for tasks')
	parser.add_argument('-u', '--user', action='store', dest='user', default='Anonymous', help='Username of helper')
	
	global args
	args = parser.parse_args()
	

def main():
	logo()
	setup()
	for t in range(args.tasks):
		print "Running task %d of %d" % (t + 1, args.tasks)
		request_task()
		load_ipaddresses()
		process_handler(ipaddresses)
		upload_results()
		time.sleep(args.wait)
	
	sys.exit()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	main()
