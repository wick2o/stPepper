#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import string

try:
	import sqlite3
except ImportError:
	print 'need some sqlite3 module'
	sys.exit()
	
try:
	from bottle import route, run,template,static_file,request,post,get
except ImportError:
	print 'need som bottle module'
	sys.exit()
	
__author__ = 'Jaime Filson aka WiK'
__license__ = 'BSD (3-Clause)'
__version__ = '0'
__date__ = ''
__maintainer__ = 'WiK'
__email__ = 'wick2o@gmail.com'
__status__ = 'Beta'

db_name = 'tasklist.db'
valid_chars = '.%s%s' % (string.ascii_letters, string.digits)
	
@get('/upload')
def upload_view():
	return """
	<form action="/upload" method="post" enctype="multipart/form-data">
	<input type="file" name="data" />
	<input type="submit" name="submit" value="upload now" />
	</form>
	""" 

@post('/upload')
def do_upload():
	global db
	data = request.files.get('data')
	if data is not None:
		raw = data.file.read() # small files =.=
		filename = data.filename
		
		t_name = ''.join(c for c in filename if c in valid_chars)
		
		if filename == t_name:
			# get ip address of the task
			c = db.cursor()
			c.execute("SELECT ip,status from tasks where task = '%s'" % (filename.replace('.done','')))
			res = c.fetchall()
			curr_status = res[0][1]
			orig_ip = res[0][0]
			new_ip = request.environ.get('REMOTE_ADDR')
			if orig_ip == new_ip:
				if curr_status != 'finished':
					f = open(filename, 'wb')
					f.write(raw)
					f.close()
					c.execute("UPDATE tasks SET status = 'finished' where task = '%s'" % (filename.replace('.done','')))
					db.commit()
					c.close()
					return "You uploaded %s (%d bytes)." % (filename, len(raw))
				else:
					c.close()
					return "This task has already been completed"
			else:
				c.close()
				return "The new ip address does not match the database..."
		else:
			c.close()
			return "Stop Messing with the site"

@get('/cancelme/<taskname>')
def cancel_task(taskname='None'):
	global db
	if taskname != 'None':
		t_taskname = ''.join(c for c in taskname if c in valid_chars)
		if t_taskname == taskname:
			c = db.cursor()
			c.execute("SELECT ip,status from tasks where task = '%s'" % (taskname))
			res = c.fetchall()
			curr_status = res[0][1]
			orig_ip = res[0][0]
			new_ip = request.environ.get('REMOTE_ADDR')
			if orig_ip == new_ip:
				if curr_status == 'assigned':
					c.execute("UPDATE tasks set status = 'open',user = 'None',ip = 'None' where task = '%s'" % (taskname))
					db.commit()
					c.close()
					return "0"
			else:
				c.close()
				return "IPSNOMATCH"
	
@route('/gettask/<name>')
def get_task(name='Anonymous'):
	global db
	t_name = ''.join(c for c in name if c in valid_chars)
	c = db.cursor()
	c.execute("SELECT task FROM tasks WHERE status = 'open' LIMIT 1")
	result = c.fetchall()
	c.execute("UPDATE tasks SET status = 'assigned', user = '%s', ip = '%s' where task = '%s'" % (t_name, request.environ.get('REMOTE_ADDR'), result[0][0]))
	db.commit()
	c.close()
	f_name = result[0][0]
	return static_file(f_name, root='tasks/', download=f_name)

@route('/')
@route('/listtasks')
def list_tasks():
	global db
	
	c = db.cursor()
	c.execute("SELECT id,task,user,status FROM tasks")
	result = c.fetchall()
	c.close()
	return template('tpl\make_table', rows=result)

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

def database_check():
	global db_name
	global db
	if os.path.exists(db_name):
		print 'Skipping database generation, %s already exists...' % (db_name)
		db = sqlite3.connect(db_name)
	else:
		print 'Database does not exist, creating %s...' % (db_name)
		db = sqlite3.connect(db_name)
		db.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, task varchar(255) NOT NULL, user varchar(100), ip varchar(25), status varchar(100))")
		db.commit()
	print ""

def main():
	logo()
	database_check()
	run(host='0.0.0.0', port=8080)
	
if __name__ == "__main__":
	main()
	
	
