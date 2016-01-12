#!/usr/bin/env python
# -*- coding: utf-8 -*-

__appname__ = "wookie"
__version__ = "v.3.2"
__author__ = "@c0ding, @grm34"
__date__ = "2012...2016"
__license__ = "Apache v2.0 License"

wookie = {
    'bot_owner': [''],
    'start_bot': 'screen -dmS wookie',
    'kill_bot': 'screen -X -S wookie kill',
    'mode': 'standard'
}

network = {
    'server': '',
    'port': 6667,
    'SSL': False,
    'ipv6': False,
    'channels': [''],
    'bot_nick': 'wookie',
    'bot_name': 'wookie v.3.2 is available at '
                'https://github.com/mrsmn/wookie',
    'password': ''
}

feeds = {
    'queue_delay': .5,
    'announce_delay': 5.0,
    'request_delay': 5.0,
    'announce': [''],
    'request': ['']
}

api = {
    'api_url': '',
    'authkey': ''
}

blacklist = {
    'announce': ['test1', 'test2', 'test3'],
    'request': ['test1', 'test2', 'test3']
}
