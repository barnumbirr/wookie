#!/usr/bin/env/python
# -*- coding: utf-8 -*-

"""
IRC RSSbot v1.2 stable
Licensed under the GNU General Public License v3

[c0da, DECEMBRE 2012]
"""

import irclib
import feedparser
from datetime import datetime
import calendar
import re
import os
import threading
import time

#CONFiG:
network = 'irc.example.com'
port = 6667
channels = ['#channel']
nick = 'botnick'
name = 'iRC-RSSBOT v1.2 (stable) available at https://github.com/c0ding/iRC-RSSbot'
password = 'nickserv password'

announce_list = ["url_feed_1"]
request_list = ["url_feed_2"]
announce_entries_file = os.environ.get("HOME") + "/.b0t/announce-entries"
request_entries_file = os.environ.get("HOME") + "/.b0t/request-entries"

#CTCP CAPABiLiTY AND DEBUG
def handleCTCP(connection, event):
	if event.arguments() [0].upper() == 'VERSION':
		connection.ctcp_reply ( event.source().split ( '!' ) [ 0 ], 'VERSION RSSBOT v1.2 (stable) available at https://github.com/c0ding/iRC-RSSbot.')
		
irclib.DEBUG = 1
irc = irclib.IRC()
irc.add_global_handler ('ctcp', handleCTCP)

#CREATE SERVER OBJECT, CONNECT TO SERVER AND JOiN CHANNELS
server = irc.server()
server.connect(network, port, nick, ircname=name, ssl=False)
if password: server.privmsg("NickServ","IDENTIFY %s" % password)
time.sleep(5)
for channel in channels:
	server.join(channel)

msgqueue = []

def announce_refresh():
 FILE = open(announce_entries_file, "r")
 filetext = FILE.read()
 FILE.close()
 for feed in announce_list:
  NextFeed = False
  d = feedparser.parse(feed)
  for entry in d.entries:
   id = entry.link.encode('utf-8')+entry.title.encode('utf-8')
   if id in filetext:
    NextFeed = True
   else:
    FILE = open(announce_entries_file, "a")
    FILE.write(id + "\n")
    FILE.close()
    title = entry.title.encode('utf-8')
    url = entry.link.encode('utf-8')
    category = title.split(' -', 1 )[0]
    title = title.split('- ', 1 )[1]
    title = title.replace(' ', '.')
    description = entry.description.encode('utf-8')
    result = re.search(r'Size : ([0-9]+\.?[0-9]*? [A-Za-z]{2})',description)
    size = result.group(1)
    entryDate = d.entries[0].published
    ReleaseDate = entryDate.split(' +', 1 )[0]
    gReleaseDate = re.search(r'Ajout&eacute; le : ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})', description)
    gPreDate = re.search(r'PreTime : ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})', description)
    if gPreDate is None:
        pretime = ""
    else:
        sPreDate = gPreDate.group(1)
        sReleaseDate = gReleaseDate.group(1)
        fmt = '%Y-%m-%d %H:%M:%S'
        releaseDate = datetime.strptime(sReleaseDate, "%Y-%m-%d %H:%M:%S")
        preDate = datetime.strptime(sPreDate, "%Y-%m-%d %H:%M:%S")
        def timestamp(date):
           return calendar.timegm(date.timetuple())
        pre = (timestamp(releaseDate)-timestamp(preDate))
        years, remainder = divmod(pre, 31556926)
        days, remainder1 = divmod(remainder, 86400)
        hours, remainder2 = divmod(remainder1, 3600)
        minutes, seconds = divmod(remainder2, 60)
		 
	if pre < 60:
        	 pretime = '%ssecs after Pre' % (seconds)
	elif pre < 3600:
        	pretime = '%smin %ssecs after Pre' % (minutes, seconds)
	elif pre < 86400:
        	pretime = '%sh %smin after Pre' % (hours, minutes)
	elif pre < 172800:
		    pretime = '%sjour %sh after Pre' % (days, hours)
	elif pre < 31556926:
        	pretime = '%sjours %sh after Pre' % (days, hours)
	elif pre < 63113852:
        	pretime = '%san %sjours after Pre' % (years, days)
	else:
   		pretime = '%sans %sjours after Pre' % (years, days)
    

    msgqueue.append("\033[37m" + "[" + "\033[31m" + category + "\033[37m" + "]" + " - " + "\033[35m" + url + title + " " + "\033[37m" + "[" + size + "] " + pretime)

 
def request_refresh():
 FILE = open(request_entries_file, "r")
 filetext = FILE.read()
 FILE.close()
 for feed in request_list:
  NextFeed = False
  d = feedparser.parse(feed)
  for entry in d.entries:
   id = entry.link.encode('utf-8')+entry.title.encode('utf-8')
   if id in filetext:
    NextFeed = True
   else:
    FILE = open(request_entries_file, "a")
    FILE.write(id + "\n")
    FILE.close()
    title = entry.title.encode('utf-8')
    url = entry.link.encode('utf-8')
    title = title.split(' - ', 1 )[0]

    msgqueue.append("\x02" + "Requests : " + "\x02" + title + " " + url)

   if NextFeed:
    break;

 t1 = threading.Timer(5.0, announce_refresh)
 t2 = threading.Timer(5.0, request_refresh)
 t1.start()
 t2.start()

announce_refresh()
request_refresh()

while 1:
 while len(msgqueue) > 0:
  msg = msgqueue.pop()
  for channel in channels:
   server.privmsg(channel, msg)
 time.sleep(1)
 irc.process_once()
 time.sleep(1)
