#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import Queue
import signal
import time
from threading import Thread, activeCount, Lock, current_thread
from subprocess import call
import urllib2
import urllib
import string
import socket

try:
	import argparse
except ImportError:
	print "Missing needed module: easy_install argparse"
	sys.exit()

try:
	from poster.encode import multipart_encode
	from poster.streaminghttp import register_openers
except ImportError:
	print "Missing needed module: easy_install poster"
	sys.exit()
	
# Import possible project files
# Code will be needed to args in setup() and and elseif in run_process()
import projects.p80search
import projects.sp1deep

__author__ = 'Jaime Filson aka WiK'
__license__ = 'BSD (3-Clause)'
__version__ = '0'
__date__ = ''
__maintainer__ = 'WiK'
__email__ = 'wick2o@gmail.com'
__status__ = 'Alpha'

task_data = []
queue = Queue.Queue()
sigint = False

wanted_results = []

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
	global args
	global f_name
	global valid_chars
	socket.setdefaulttimeout(60)
	try:
		if args.debug:
			print 'Attempting to connect to http://%s/gettask/%s/%s' % (args.server, args.user, args.project)
	
		res = urllib2.urlopen('http://%s/gettask/%s/%s' % (args.server, args.user, args.project))
	
	except (urllib2.HTTPError, urllib2.URLError) as err:
		print 'Server has not responded, please check your ip address'
		sys.exit()
		
	f_name = res.info()['Content-Disposition'].split('filename=')[1].replace('"','')
	t_name = ''.join(c for c in f_name if c in valid_chars)
	
	if args.debug:
		print 'Validating filename...'
		print '\tString from Server: %s' % (f_name)
		print '\tString from Validation: %s' % (t_name)

	if f_name == t_name:
		if args.debug:
			print 'Strings Match! Writing contents to %s' % (f_name)
		f_content = res.read()
		f = open(f_name, 'wb')
		f.write(f_content)
		f.close()
	else:
		print 'Error: Filename from server does not match a legit filename'
		sys.exit()
	
	res.close()
	
	
def load_task_data():
	global f_name
	
	td_file = open(f_name,'r')
	td_read = td_file.readlines()
	td_read = [item.rstrip() for item in td_read]
	for itm in td_read:
		if not itm.startswith('#'): #ignore comments
			task_data.append(itm)
	td_file.close()
	

def run_process(project,itm):
	if project == 'p80search':
		x = projects.p80search.p80search()
		res = x.process_single(itm)
		if res == True:
			wanted_results.append(itm)
	elif project == 'sp1deep':
		x = projects.sp1deep.sp1deep()
		res = x.process_single(itm)
		for lnk in res:
			wanted_results.append(lnk)

def upload_results():
	global f_name
	socket.setdefaulttimeout(60)
	print "Completed Task: %s" % (f_name)
	df = '%s.done' % (f_name)
	f = open(df, 'wb')
	f.write('\n'.join(wanted_results))
	f.close()
	url = 'http://%s/upload' % (args.server)
	register_openers()
	f = open(df, 'rb')
	datagen, headers = multipart_encode({'data': f})
	try:
		request = urllib2.Request(url,datagen,headers)
		print urllib2.urlopen(request).read()
	except:
		print "Some kind of error uploading..."
		res = urllib2.urlopen('http://%s/cancelme/%s' % (args.server,f_name))
	f.close()
	if os.path.exists(f_name) and not args.debug:
		os.remove(f_name)
	if os.path.exists(df) and not args.debug:
		os.remove(df)

def progressbar(progress, total):
	global args
	if not args.quite:
		progress_percentage = int(100 / (float(total) / float(progress)))
		total = float(total)
		#calculate progress for 25, 50, 75, and 99%
		vals = [
				int(total/100*10),
				int(total/100*20),
				int(total/100*30),
				int(total/100*40),
				int(total/100*50), 
				int(total/100*60), 
				int(total/100*70),
				int(total/100*80),
				int(total/100*90),				
				int(total-1)
				]
		if progress in vals:
			sys.stdout.write("%s %s%% complete\r" % (("#"*(progress_percentage / 10)), progress_percentage))

def process_handler(task_data):
	global args
	
	progress = 0
	
	if args.threads > 1:
		threads = []
		for itm in task_data:
			queue.put(itm)
		progress_lock = Lock()

		while not queue.empty() and not sigint:
			if args.threads >= activeCount() and not sigint:
				q_itm = queue.get()
				try:
					# setup thread to run process
					t = Thread(target=run_process,args=(args.project,q_itm,))
					t.daemon = True
					threads.append(t)
					t.start()
				finally:
					progress = len(task_data) - queue.qsize()
					
					progress_lock.acquire()
					try:
						progressbar(progress, len(task_data))
					finally:
						progress_lock.release()
					queue.task_done()
		while activeCount() > 1:
			time.sleep(0.1)
		for thread in threads:
			thread.join()

		queue.join()
	else:
		for itm in task_data:
			run_process(args.project,itm)
			progress = progress + 1
			progressbar(progress, len(task_data))
			if sigint == True:
				signal_handler('','')
	return


def signal_handler(signal, frame):
	global args
	if args.debug:
		print 'Running the signal_handler function...'
	#handles ctrl+c events
	global sigint
	global f_name
	sigint = True
		
	print ' Ctrl+C detected... exiting...\n'
	
	try:
		socket.setdefaulttimeout(60)
		if args.debug:
			print 'Attempting to tell server to reset my chunk by calling http://%s/cancelme/%s' % (args.server,f_name)
		res = urllib2.urlopen('http://%s/cancelme/%s' % (args.server,f_name))
	except:
		pass
	
	# cleanup from canceled task
	if args.debug:
		print 'Attempting to delete the chunk file if it exists...'
	if os.path.exists(f_name) and not args.debug:
		os.remove(f_name)
		
	cleanup()
	sys.exit(1)
	
def cleanup():
	for root,dirs, files in os.walk('projects'):
		for file in files:
			if os.path.splitext(file)[1] == '.pyc':
				os.remove(os.path.join(root, file))

def setup():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--threads', action='store', dest='threads', default=0, type=int, help='Enable threading. Specifiy max # of threads')
	parser.add_argument('-m', '--maxtasks', action='store', dest='tasks', default=1, type=int, help='Max tasks to complete in a row')
	parser.add_argument('-w', '--wait', action='store', dest='wait', default=0, type=int, help='Wait time between tasks in seconds')
	parser.add_argument('-s', '--server', action='store',dest='server', required=True, help='IP address of the server for tasks')
	parser.add_argument('-u', '--user', action='store', dest='user', default='Anonymous', help='Username of helper')
	parser.add_argument('-p', '--project', action='store', dest='project', choices=['p80search','sp1deep'], default='p80search', help='Project to run')
	
	verbose_group = parser.add_mutually_exclusive_group()
	verbose_group.add_argument('-d', '--debug', action='store_true', dest='debug', help='Show Debug Messages')
	verbose_group.add_argument('-q', '--quite', action='store_true', dest='quite', help='Hide General Messages')
		
	global args
	args = parser.parse_args()
	
	try:
		socket.inet_aton(args.server.split(':')[0])
	except:
		print 'Error: The ip address is not valid'
		cleanup()
		sys.exit()
		
	

def main():
	global wanted_results
	global task_data
	global args
	
	setup()
	if not args.quite:
		logo()
	
	for t in range(args.tasks):
		print "Running task %d of %d" % (t + 1, args.tasks)
		task_data = []
		wanted_results = []

		request_task()
		load_task_data()
		process_handler(task_data)
		upload_results()
		time.sleep(args.wait)
		
		
	cleanup()
	sys.exit()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	main()
