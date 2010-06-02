# Copyright (c) Daniel Richman 2010

from Queue import Queue
import sys

from dummy import Stream
from bot import IRCBot
import config

def debug(s):
  sys.stderr.write("%s\n" % s)

def main():
  queue = Queue()

  debug("Main: Setting up")
  bot = IRCBot(config, queue, debug)
  stream = Stream(config, queue, debug)

  debug("Starting...")
  bot.start()
  stream.start()

main()
