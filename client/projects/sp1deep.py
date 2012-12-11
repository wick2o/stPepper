#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import urllib2
import re

class sp1deep:
	def process_single(self, ip):
		found = []
		try:
			socket.setdefaulttimeout(5)
			url = 'http://%s' % (ip)
			req = urllib2.Request(url)
			req.add_header('User-Agent', 'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1')
			try:
				page = urllib2.urlopen(req)
			except:
				page = 'err'
			finally:
				if page != 'err':
					page_res = page.read()
					page.close()
					links = re.findall(r"<a.*?\s*href=\"(.*?)\".*?>(.*?)</a>", page_res)
					for link in links:
						found.append('%s\n' % (link[0]))
					return found
				else:
					return found
		except:
			return found
