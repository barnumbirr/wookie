#!/usr/bin/python
# IRC RSSbot v0.4

import irclib
import feedparser
from datetime import datetime
import calendar
import re
import os
import threading
import time

channel_list = [ "#channel" ] 
feed_list = [ "rss_feed"]
old_entries_file = os.environ.get("HOME") + "/.b0t/old-feed-entries"

irc = irclib.IRC()
server = irc.server()

server.connect( "host", 6667, "nick" ) 
server.privmsg( "NickServ", "identify password" )

msgqueue = []

def feed_refresh():
 #print "Test"
 FILE = open( old_entries_file, "r" )
 filetext = FILE.read()
 FILE.close()
 for feed in feed_list:
  NextFeed = False
  d = feedparser.parse( feed )
  for entry in d.entries:
   id = entry.link.encode('utf-8')+entry.title.encode('utf-8')
   if id in filetext:
    NextFeed = True
   else:
    FILE = open( old_entries_file, "a" )
    #print entry.title + "\n"
    FILE.write( id + "\n" )
    FILE.close()
    #######################################################
    #personnal usage, most users won't need this
    #######################################################
    #title = entry.title.encode('utf-8')
    #url = entry.link.encode('utf-8')
    #category = title.split(' -', 1 )[0]
    #title = title.split('- ', 1 )[1]
    #title = title.replace(' ', '.')
    #description = entry.description.encode('utf-8')
    #result = re.search(r'Size : ([0-9]+\.?[0-9]*? [A-Za-z]{2})',description)
    #size = result.group(1)
    #entryDate = d.entries[0].published
    #ReleaseDate = entryDate.split(' +', 1 )[0]
    #gReleaseDate = re.search(r'Ajout&eacute; le : ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})', description)
    #gPreDate = re.search(r'PreTime : ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})', description)
    #if gPreDate is None:
    #    pretime = ""
    #else:
    #   sPreDate = gPreDate.group(1)
    #    sReleaseDate = gReleaseDate.group(1)
    #    fmt = '%Y-%m-%d %H:%M:%S'
    #    releaseDate = datetime.strptime(sReleaseDate, "%Y-%m-%d %H:%M:%S")
    #    preDate = datetime.strptime(sPreDate, "%Y-%m-%d %H:%M:%S")
    #    def timestamp(date):
    #       return calendar.timegm(date.timetuple())
    #    pre = (timestamp(releaseDate)-timestamp(preDate))
    #    years, remainder = divmod(pre, 31556926)
    #    days, remainder1 = divmod(remainder, 86400)
    #    hours, remainder2 = divmod(remainder1, 3600)
    #    minutes, seconds = divmod(remainder2, 60)
    #
    #if pre < 60:
    #   pretime = '%ssecs after Pre' % (seconds)
    #elif pre < 3600:
    #   pretime = '%smin %ssecs after Pre' % (minutes, seconds)
    #elif pre < 86400:
    #   pretime = '%sh %smin after Pre' % (hours, minutes)
    #elif pre < 172800:
    #   pretime = '%sjour %sh after Pre' % (days, hours)
    #elif pre < 31556926:
    #   pretime = '%sjours %sh after Pre' % (days, hours)
    #elif pre < 63113852:
    #   pretime = '%san %sjours after Pre' % (years, days)
    #else:
    #   pretime = '%sans %sjours after Pre' % (years, days)
    #
    #msgqueue.append("[" + category + "]" + " - " + url + title + " [" + size + "] " + pretime)
    #######################################################

    msgqueue.append( entry.title.encode('utf-8') + " : " + entry.link.encode('utf-8') )

   if NextFeed:
     break;

 t = threading.Timer( 5.0, feed_refresh ) 
 t.start()

for channel in channel_list:
  server.join( channel )

feed_refresh()

while 1:
 while len(msgqueue) > 0:
  msg = msgqueue.pop()
  for channel in channel_list:
   server.privmsg( channel, msg )
 time.sleep(1) 
 irc.process_once()
 time.sleep(1)