#!/usr/bin/env python
# -*- coding=utf-8 -*-


import urllib
import urllib2



test = '検索'
q = urllib.urlencode({'q':test})
print q

url = "http://ja.wikipedia.org/wiki/%s"%(q[2:],)
req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
h = urllib2.urlopen(req)
data = h.read()

with open('test', 'w') as f:
    f.write(data)


