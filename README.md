<h1><img src="https://raw.githubusercontent.com/mrsmn/wookie/master/doc/wookie.png" height=70 alt="wookie" title="wookie">wookie</a></h1>

**wookie** is a simple, open source, easy-to-use iRC RSS bot written in Python.
It was designed to announce new torrent releases in a given iRC channel.

## Features

* Easy configuration
* No heavy database required
* SSL support
* Support for additional commands
* Blacklist entries
* IRC Colors
* API Search

## Required:

```
$ apt-get install python-pip  
$ pip install feedparser django  
$ wget http://sourceforge.net/projects/python-irclib/files/python-irclib/0.4.8/python-irclib-0.4.8.tar.gz  
$ tar -zxvf python-irclib-0.4.8.tar.gz && rm python-irclib-0.4.8.tar.gz && cd python-irclib-0.4.8  
$ python setup install
```

## Installation:

```
$ cd /home/<username>  
$ git clone https://github.com/mrsmn/wookie.git  
$ cd wookie/wookie
```

Edit the config.py file to suit your needs, then:

```
$ python wookie.py <start> or <screen>
```

## Awesome contributors:

* [grm34](https://github.com/grm34)

## License

```
  Apache v2.0 License
  Copyright 2012-2016 Martin Simon, Jérémy Pardo

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

```

## Buy me a coffee?

If you feel like buying me a coffee (or a beer?), donations are welcome:

```
WDC : WbcWJzVD8yXt3yLnnkCZtwQo4YgSUdELkj
HBN : F2Zs4igv8r4oJJzh4sh4bGmeqoUxLQHPki
DOGE: DRBkryyau5CMxpBzVmrBAjK6dVdMZSBsuS
```

All credit for the wookie icon goes to <a href="http://www.jameshance.com/">James Hance</a>.
