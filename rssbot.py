#!/usr/bin/python
#iRC RSSbot v0.3

import irclib
import feedparser
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
    ############################################################
    #personnal usage, most users won't need this
    ############################################################
    #title = entry.title.encode('utf-8')
    #url = entry.link.encode('utf-8')
    #category = title.split(' -', 1 )[0]
    #title = title.split('- ', 1 )[1]
    #title = title.replace(' ', '.')
    #description = entry.description.encode('utf-8')
    #result = re.search(r'Size : ([0-9]+\.?[0-9]*? [A-Za-z]{2})',description)
    #size = result.group(1)
    #msgqueue.append("[" + category + "]" + " - " + url + title + " [" + size + "]")
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
 time.sleep(1) # TODO: Fix bad code
 irc.process_once()
 time.sleep(1)