#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ssl
import json
import time
import irclib
import socket
import urllib2
import calendar
import commands
import optparse
import threading
import feedparser
from json import loads
from irclib import SimpleIRCClient
from threading import (Thread, Event)
from datetime import (datetime, timedelta)
from django.utils.encoding import smart_str
from urllib2 import (urlopen, URLError, HTTPError)
from config import (feeds, wookie, network, api, blacklist)

__appname__ = "wookie"
__version__ = "v.3.2"
__author__ = "@c0ding, @grm34"
__date__ = "2012...2016"
__license__ = "Apache v2.0 License"


class Queue_Manager(Thread):

    def __init__(self, connection, delay=feeds['queue_delay']):
        Thread.__init__(self)
        self.setDaemon(1)
        self.connection = connection
        self.delay = delay
        self.event = Event()
        self.queue = []

    def run(self):
        while 1:
            self.event.wait()
            while self.queue:
                (msg, target) = self.queue.pop(0)
                self.connection.privmsg(target, msg)
                time.sleep(self.delay)
            self.event.clear()

    def send(self, msg, target):
        self.queue.append((msg.strip(), target))
        self.event.set()


class _wookie(SimpleIRCClient):

    def __init__(self):
        irclib.SimpleIRCClient.__init__(self)
        self.start_time = time.time()
        self.queue = Queue_Manager(self.connection)

        self.BLACK = '\x0301'
        self.BLUE = '\x0302'
        self.RED = '\x0304'
        self.YELLOW = '\x0308'
        self.GREEN = '\x0303'
        self.PURPLE = '\x0306'
        self.PINK = '\x0313'
        self.ORANGE = '\x0307'
        self.TEAL = '\x0310'
        self.BOLD = '\x02'
        self.ITALIC = '\x1D'
        self.UNDERLINE = '\x1F'
        self.SWAP = '\x16'
        self.END = '\x0F'

    def on_welcome(self, serv, ev):
        if network['password']:
            serv.privmsg(
                "nickserv", "IDENTIFY {}".format(network['password']))
            serv.privmsg("chanserv", "SET irc_auto_rejoin ON")
            serv.privmsg("chanserv", "SET irc_join_delay 0")
        for channel in network['channels']:
            serv.join(channel)
        try:
            self.history_manager()
            self.announce_refresh()
            self.request_refresh()
            time.sleep(5)
            self.queue.start()
        except (OSError, IOError) as error:
            serv.disconnect()
            print(error)
            sys.exit(1)

    def on_rss_entry(self, text):
        for channel in network['channels']:
            self.queue.send(text, channel)

    def on_kick(self, serv, ev):
        serv.join(ev.target())

    def on_invite(self, serv, ev):
        serv.join(ev.arguments()[0])

    def on_ctcp(self, serv, ev):
        if ev.arguments()[0].upper() == 'VERSION':
            serv.ctcp_reply(
                ev.source().split('!')[0], network['bot_name'])

    def history_manager(self):
        home = '{}/.wookie_logs'.format(os.environ.get('HOME'))
        self.wookie_path = os.path.dirname(os.path.realpath(__file__))
        self.announce_entries = '{}/announce-entries'.format(home)
        self.request_entries = '{}/request-entries'.format(home)
        self.irc_entries = '{}/irc-entries'.format(home)
        if os.path.exists(home) is False:
            os.system('mkdir {}'.format(home))
        if os.path.exists(self.announce_entries) is False:
            os.system('touch {}'.format(self.announce_entries))
        if os.path.exists(self.request_entries) is False:
            os.system('touch {}'.format(self.request_entries))
        if os.path.exists(self.irc_entries) is False:
            os.system('touch {}'.format(self.irc_entries))

    def restart_bot(self, serv, ev):
        serv.disconnect()
        if wookie['mode'] == 'screen':
            current_screen = self.get_current_screen()
            os.system('{0} {1}/./wookie.py run && screen -X -S {2} kill'
                      .format(wookie['start_bot'], self.wookie_path,
                              current_screen))
        else:
            os.system('{}/./wookie.py start'.format(self.wookie_path))
        sys.exit(1)

    def get_current_screen(self):
        screen_list = commands.getoutput('screen -list')
        screen_lines = smart_str(
            screen_list.replace('\t', '')).splitlines()
        for screen in screen_lines:
            if 'wookie' in screen:
                current_screen = screen.split('.')[0]
        return current_screen

    def timestamp(self, date):
        return calendar.timegm(date.timetuple())

    def get_nice_size(self, num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def get_rls_pretime(self, pre):
        (years, remainder) = divmod(pre, 31556926)
        (days, remainder1) = divmod(remainder, 86400)
        (hours, remainder2) = divmod(remainder1, 3600)
        (minutes, seconds) = divmod(remainder2, 60)
        if pre < 60:
            pretime = '{}secs after Pre'.format(seconds)
        elif pre < 3600:
            pretime = '{0}min {1}secs after Pre'.format(minutes, seconds)
        elif pre < 86400:
            pretime = '{0}h {1}min after Pre'.format(hours, minutes)
        elif pre < 172800:
            pretime = '{0}jour {1}h after Pre'.format(days, hours)
        elif pre < 31556926:
            pretime = '{0}jours {1}h after Pre'.format(days, hours)
        elif pre < 63113852:
            pretime = '{0}an {1}jours after Pre'.format(years, days)
        else:
            pretime = '{0}ans {1}jours after Pre'.format(years, days)
        return pretime

    def search_release(self, serv, ev, message, chan):
        data = loads(urlopen('{0}{1}{2}{3}{4}{5}'.format(
            api['api_url'], 'torrent/search&ak=',
            api['authkey'], '&q=',
            smart_str(message[5:].replace(' ', '+').replace('.', '+')),
            '&nb=1'), None, 5.0).read())

        id = smart_str(data[0]['id'])
        title = smart_str(data[0]['name']).replace(' ', '.')
        url = '{0}{1}{2}/{3}'.format(
            api['api_url'].replace('api/', ''),
            'torrent/', id, title)
        completed = smart_str(data[0]['times_completed'])
        leechers = smart_str(data[0]['leechers'])
        seeders = smart_str(data[0]['seeders'])
        added = smart_str(data[0]['added'])
        comments = smart_str(data[0]['comments'])
        size = self.get_nice_size(int(data[0]['size']))
        predate = smart_str(data[0]['pretime'])
        pretime = ''
        if predate != '0':
            releaseDate = datetime.strptime(
                added, '%Y-%m-%d %H:%M:%S')
            pre = (self.timestamp(releaseDate)-(int(predate)+3600))
            pretime = ' | {0}Pretime:{1} {2}'.format(
                self.BOLD, self.END, self.get_rls_pretime(int(pre)))

        serv.privmsg(chan, '{0}{1}:{2} {3}'.format(
            self.BOLD, title, self.END, url))
        serv.privmsg(
            chan, '{7}Added on:{8} {0}{1} | {7}Size:{8} {2} '
            '| {7}Seeders:{8} {3} | {7}Leechers:{8} {4} '
            '| {7}Completed:{8} {5} | {7}Comments:{8} {6}'
            .format(added, pretime, size, seeders,
                    leechers, completed, comments, self.BOLD, self.END))

    def on_privmsg(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0].strip()
        arguments = message.split(' ')
        if author in wookie['bot_owner']:
            if '.say' == arguments[0] and len(arguments) > 2:
                serv.privmsg(
                    arguments[1], message.replace(arguments[0], '')
                                         .replace(arguments[1], '')[2:])
            if '.act' == arguments[0] and len(arguments) > 2:
                serv.action(
                    arguments[1], message.replace(arguments[0], '')
                                         .replace(arguments[1], '')[2:])
            if '.join' == arguments[0] and len(arguments) > 2:
                serv.join(message[3:])
            if '.part' == arguments[0] and len(arguments) > 2:
                serv.part(message[3:])

    def on_pubmsg(self, serv, ev):
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0].strip()
        arguments = message.split(' ')
        event_time = time.strftime('[%H:%M:%S]', time.localtime())
        record = '{0} {1}: {2}'.format(event_time, author, message)
        FILE = open(self.irc_entries, "a")
        FILE.write("{}\n".format(record))
        FILE.close()
        print (record)
        chan = ev.target()
        if author in wookie['bot_owner']:
            try:
                if ev.arguments()[0].lower() == '.restart':
                    self.restart_bot(serv, ev)
                if ev.arguments()[0].lower() == '.quit':
                    serv.disconnect()
                    if not wookie['mode']:
                        os.system(wookie['kill_bot'])
                    sys.exit(1)
            except OSError as error:
                serv.disconnect()
                print(error)
                sys.exit(1)

        if '.help' == arguments[0].lower():
            serv.privmsg(
                chan, '{0}{2}{3}Available commands:{1}{0} .help || '
                      '.version || .uptime || .restart || .quit || '
                      '.get <release>{1}'.format(
                            self.BOLD, self.END, self.UNDERLINE, self.BLUE))

        if '.version' == arguments[0].lower():
            serv.privmsg(chan, '{0}{1}{2}{3}'.format(
                self.BOLD, self.PINK, network['bot_name'], self.END))

        if '.uptime' == arguments[0].lower():
            uptime_raw = round(time.time() - self.start_time)
            uptime = timedelta(seconds=uptime_raw)
            serv.privmsg(chan, '{0}{3}[UPTIME]{4} {2}{1}'.format(
                    self.BOLD, self.END, uptime, self.TEAL, self.BLACK))

        if '.get' == arguments[0].lower() and len(arguments) > 1:
            try:
                self.search_release(serv, ev, message, chan)
            except (HTTPError, URLError, KeyError,
                    ValueError, TypeError, AttributeError):
                serv.privmsg(
                    chan, '{0}Nothing found, sorry about this.{1}'.format(
                        self.BOLD, self.END))
                pass
            except socket.timeout:
                serv.privmsg(
                    chan, "{0}{1}[ERROR]{2} API timeout...".format(
                        self.BOLD, self.RED, self.END))
                pass

    def announce_refresh(self):
        FILE = open(self.announce_entries, "r")
        filetext = FILE.read()
        FILE.close()

        for feed in feeds['announce']:
            d = feedparser.parse(feed)
        for entry in d.entries:
            id_announce = '{0}{1}'.format(smart_str(entry.link),
                                          smart_str(entry.title))
            if id_announce not in filetext and\
                    any([x not in id_announce for x in blacklist['announce']]):
                url = smart_str(entry.link)
                title = smart_str(
                    entry.title).split(' - ', 1)[1].replace(' ', '.')
                size = smart_str(
                    entry.description).split('|')[1].replace(
                        'Size :', '').strip()
                category = smart_str(entry.title).split(' -', 1)[0]\
                                                 .replace(' ', '-')
                if len(entry.description.split('|')) == 5:
                    pretime = ''
                else:
                    releaseDate = datetime.strptime(smart_str(
                        entry.description).split('|')[2].replace(
                            smart_str('Ajouté le :'), '').strip(),
                        '%Y-%m-%d %H:%M:%S')
                    preDate = datetime.strptime(smart_str(
                        entry.description).split('|')[5].replace(
                            'PreTime :', '').strip(),
                        '%Y-%m-%d %H:%M:%S')
                    pre = (
                        self.timestamp(releaseDate)-self.timestamp(preDate))
                    pretime = self.get_rls_pretime(pre)

                self.on_rss_entry(
                    '{5}{6}[{0}] {10}{1}{2} {8}[{3}] {9}{4}{7}'.format(
                        category, url, title, size, pretime, self.BOLD,
                        self.RED, self.END, self.GREEN, self.YELLOW,
                        self.BLACK))
                FILE = open(self.announce_entries, "a")
                FILE.write("{}\n".format(id_announce))
                FILE.close()

        threading.Timer(
            feeds['announce_delay'], self.announce_refresh).start()

    def request_refresh(self):
        FILE = open(self.request_entries, "r")
        filetext = FILE.read()
        FILE.close()

        for feed in feeds['request']:
            d = feedparser.parse(feed)
        for entry in d.entries:
            id_request = '{0}{1}'.format(
                smart_str(entry.link),
                smart_str(entry.title).split(' - ')[0].replace(' ', '.'))
            if id_request not in filetext and\
                    any([x not in id_request for x in blacklist['request']]):
                title = smart_str(
                    entry.title).split(' - ', 1)[0].replace(' ', '.')
                url = smart_str(entry.link)
                self.on_rss_entry(
                    '{2}{4}[REQUEST]{3} {0} {6}{1}{5}'.format(
                        title, url, self.BOLD, self.BLACK,
                        self.PURPLE, self.END, self.BLUE))
                FILE = open(self.request_entries, "a")
                FILE.write('{}\n'.format(id_request))
                FILE.close()

        threading.Timer(
            feeds['request_delay'], self.request_refresh).start()


def main():

    usage = './wookie.py <start> or <screen>\n\n'\
        '<start> to run wookie in standard mode\n'\
        '<screen> to run wookie in detached screen'
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if len(args) == 1 and (
            args[0] == 'start' or
            args[0] == 'screen' or
            args[0] == 'run'):
        bot = _wookie()
    else:
        parser.print_help()
        parser.exit(1)

    try:
        if args[0] == 'screen':
            wookie['mode'] = 'screen'
            os.system('{0} {1}/./wookie.py run'.format(
                wookie['start_bot'], os.path.dirname(
                    os.path.realpath(__file__))))
            sys.exit(1)

        bot.connect(
            network['server'], network['port'],
            network['bot_nick'], network['bot_name'],
            ssl=network['SSL'], ipv6=network['ipv6'])
        bot.start()

    except OSError as error:
        print(error)
        sys.exit(1)
    except irclib.ServerConnectionError as error:
        print (error)
        sys.exit(1)

if __name__ == "__main__":
    main()
