# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys

from stream import Stream
from bot import IRCBot
import config

def debug(s):
  sys.stderr.write("%s\n" % s)

def main():
  debug("Main: Setting up...")
  bot = IRCBot(config.irc, debug)
  stream = Stream(config.twitter, bot.queue_message, debug)

  debug("Starting...")
  bot.start()
  stream.start()

main()
