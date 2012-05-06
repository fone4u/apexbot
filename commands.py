# Copyright 2011 Priyesh Patel

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import json
import urllib
import urllib2
import re
from htmlentitydefs import name2codepoint
name2codepoint['#39'] = 39

from config import commands

class Commands:
    def __init__(self, channel, info, callback):
        self.channel = channel
        self.info = info
        self.callback = callback
        self.config = commands

        self.commands = {
                "h" : self.help,
                "help" : self.help,
                "p" : self.paste,
                "paste" : self.paste,
                "pastie" : self.paste,
                "g" : self.search,
                "google" : self.search,
                "search" : self.search,
                "c" : self.calculator,
                "calc" : self.calculator,
                "calculator" : self.calculator
                }

    def parse(self, cmd, args, origin):
        self.origin = origin

        self.info("Command: Parsing...")       
        self.cmd = cmd
        self.args = args

        self.args = self.args.strip(" \t\n\r")
        self.origin = self.origin.partition("!")[0]

        try:
            self.commands[cmd]()
        except:
            self.info("Command: Not found")

    def help(self):
        self.callback("%s: ApexBot currently supports the following commands: paste warning (!p/!paste/!pastie), Google search (!g/!google/!search) and calculator (!c/!calc/!calculator)" % self.origin, self.channel)

    def paste(self):
        if self.args != "":
            self.callback("%s: Do not paste in the channel, please use http://pastie.org" % self.args, self.channel)
        else:
            self.callback("Do not paste in the channel, please use http://pastie.org", self.channel)

    def search(self):
        if self.args == "":
            self.info("Command: No search term entered")
            self.callback("%s: Please enter a search term" % self.origin, self.channel)
            return

        self.info("Command: Searching Google for \"%s\"" % self.args)

        searchstring = urllib.quote(self.args, '')
        url = "https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&key=%s&safe=moderate" % (searchstring, self.config.googleapi)

        self.info("Command: Requesting url: %s" % url)

        try:
            data = urllib2.urlopen(url)
            decodeddata = json.load(data)
            data.close()
            result = (re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), decodeddata['responseData']['results'][0]['titleNoFormatting'].encode('utf-8')), decodeddata['responseData']['results'][0]['url'].encode('utf-8'))
            self.info("Command: Sending results")
            self.callback("%s: %s" % (self.origin, result[0]), self.channel)
            self.callback("%s: %s" % (self.origin, result[1]), self.channel)
        except:
            self.info("Command: Failed to get url or no results")
            self.callback("%s: No results" % self.origin, self.channel)

    def calculator(self):
        if self.args == "":
            self.info("Command: No calculation entered")
            self.callback("%s: Please enter a calculation" % self.origin, self.channel)
            return

        self.info("Command: Calculating %s" % self.args)

        if not self.args.find("**") == -1:
            self.info("Command: Calculation not allowed")
            self.callback("%s: Calculation not allowed" % (self.origin), self.channel)
            return

        try:
            result = str(eval(self.args))
            self.info("Command: Answer = %s" % result)
            self.callback("%s: %s" % (self.origin, result), self.channel)
        except:
            self.info("Command: Calculation invalid")
            self.callback("%s: Calculation invalid" % self.origin, self.channel)
