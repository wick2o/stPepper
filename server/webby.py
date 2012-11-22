#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

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
    name = request.forms.get('name')
    data = request.files.get('data')
    if data is not None:
        raw = data.file.read() # small files =.=
        filename = data.filename
		# block all /, ../, anything non alphanum
		if re.search("^[A-Za-z0-9]+\.done$", filename) == None:
			return "Go away"
        f = open(filename, 'wb')
        f.write(raw)
        f.close()
        conn = sqlite3.connect('tasklist.db')
        c = conn.cursor()
		if filename.find("'") != -1:
			c.close()
			return "Go away"
        c.execute("UPDATE todo SET status = 'finished' where task = '%s'" % (filename.replace('.done','')))
        conn.commit()
        c.close()
        conn.close()
        return "Hello %s! You uploaded %s (%d bytes)." % (name, filename, len(raw))
    return "You missed a field."
	
@route('/gettask')
def get_task():
	conn = sqlite3.connect('tasklist.db')
	c = conn.cursor()
	c.execute("SELECT task FROM todo WHERE status = 'open' LIMIT 1")
	result = c.fetchall()
	c.execute("UPDATE todo SET status = 'assigned' where task = '%s'" % (result[0][0]))
	conn.commit()
	c.close()
	conn.close()
	f_name = result[0][0]
	return static_file(f_name, root='tasks/', download=f_name)

@route('/')
@route('/listtasks')
def list_tasks():
	conn = sqlite3.connect('tasklist.db')
	c = conn.cursor()
	c.execute("SELECT * FROM todo")
	result = c.fetchall()
	c.close()
	conn.close()
	return template('make_table', rows=result)


	
run(host='172.16.1.10', port=8080, reloader=True)