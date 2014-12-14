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
	'ipv6': False,
	'channels': ['#channel'],
	'bot_nick': 'wookie',
	'bot_name': 'wookie v.3.0 is available at https://github.com/c0ding/wookie',
	'password': ''
}

feeds = {
    'delay': .5,
    'announce': ['https://example.com/rss/feeds1'],
    'request': ['https://example.com/rss/feeds2']
}

wookie = {
	'bot_owner': ['maybe_you_!'],
	'path': '/path/to/wookie/dir/',
	'start_bot': 'screen -dmS wookie',
	'kill_bot': 'screen -X -S wookie kill',
	'mode': '' # Leave this empty !
}
