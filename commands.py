# Copyright 2011 Priyesh Patel

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

class Commands:
    def __init__(self, channel, info, callback):
        self.channel = channel
        self.info = info
        self.callback = callback

    def parse(self, cmd, args, origin):
        self.origin = origin

        self.info("Command: Parsing...")       
        self.cmd = cmd
        self.args = args

        self.args = self.args.strip(" \t\n\r")
        self.origin = self.origin.partition("!")[0]

        if (self.cmd == "parse") or (self.cmd == "__init__"):
            self.info("Command: Not found.")
            return 

        if hasattr(self, self.cmd):
            self.info("Command: Command found. Executing...")
            getattr(self, self.cmd)()
        else:
            self.info("Command: Not found.")

    def p(self):
        self.paste()

    def pastie(self):
        self.paste()

    def paste(self):
        if self.args != "":
            self.callback("%s: Do not paste in the channel. Please use http://pastie.org" % self.args, self.channel)
        else:
            self.callback("Do not paste in the channel. Please use http://pastie.org", self.channel)

    def g(self):
        self.google()

    def search(self):
        self.google()

    def google(self):
        if self.args == "":
            self.info("Command: No search term entered.")
            self.callback("%s: Please enter a search term." % self.origin, self.channel)
            return

        self.info("Command: Searching Google for \"%s\"." % self.args)
        self.callback("%s: Searching Google for \"%s\"." % (self.origin, self.args), self.channel)
