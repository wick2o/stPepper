#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import urllib2

class p80search:
	def process_single(self, ip):
		try:
			socket.inet_aton(ip)
			socket.setdefaulttimeout(2)
			url = 'http://%s' % (ip)
			req = urllib2.Request(url)
			req.add_header('User-Agent', 'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1')
			try:
				res = urllib2.urlopen(req)
				return True
			except:
				return False

		except:
			return False
