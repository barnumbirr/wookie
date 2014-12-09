#!/usr/bin/env python
# -*- coding: utf-8 -*-

__appname__ = "wookie"
__version__ = "v.2.2"
__author__  = "@c0ding"
__date__    = "October 2014"
__license__ = "Apache v2.0 License"

network = {
	'server': 'irc.example.net',
	'port': 6667,
	'SSL': False,
	'channels': ['#channel'],
	'bot_nick': 'wookie',
	'bot_name': 'wookie v.2.2 is available at https://github.com/c0ding/wookie',
	'password': ''
}

feeds = {
	'announce': ['https://example.com/rss/feed1'],
	'request': ['https://example.com/rss/feed2']
}

wookie = {
	'path': 'path/to/wookie/dir'
}
