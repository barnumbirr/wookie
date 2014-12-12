#!/usr/bin/env python
# -*- coding: utf-8 -*-

__appname__ = "wookie"
__version__ = "v.3.0"
__author__  = "@c0ding, @grm34"
__date__    = "2012 - 2014"
__license__ = "Apache v2.0 License"

network = {
	'server': 'irc.example.net',
	'port': 6667,
	'SSL': False,
	'channels': ['#channel'],
	'bot_nick': 'wookie',
	'bot_name': 'wookie v.3.0 is available at https://github.com/c0ding/wookie',
	'password': ''
}

feeds = {
	'delay': .5
	'announce': ['https://example.com/rss/feed1'],
	'request': ['https://example.com/rss/feed2']
}

wookie = {
	'path': 'path/to/wookie/dir'
}
