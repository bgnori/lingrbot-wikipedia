#!/usr/bin/env python
# -*- coding=utf-8 -*-


from lxml import etree
parser = etree.HTMLParser()

#get p just before toc

with open('test') as f:
    t = etree.parse(f, parser)
    found = t.xpath('//table[@id="toc"]')
    assert len(found) == 1
    table = found[0]
    for n in table.xpath('preceding-sibling::p'):
        print etree.tostring(n)

    
    
