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
import Queue
from daemon import DaemonThread
import time
import threading

import irclib

def action_message(act):
  return "\x01ACTION %s \x01" % act

class IRCBot:
  def __init__(self, config, debug):
    debug("IRC: Setting up...")

    self.irc = irclib.IRC();
    self.config = config
    self.debug = debug
    self.queue = Queue.Queue()

    self.reconnects = 0
    self.dead = threading.Event()

    self.msglock = threading.Lock()

    self.channels = []

  def start(self):
    self.debug("IRC: Starting...")
    DaemonThread(target=self.main).start()
    DaemonThread(target=self.process_queue).start()

  def main(self):
    self.debug("IRC: Running!")

    while True:
      try:
        self.connect()

        while True:
          self.irc.process_once(1)

          if self.dead.isSet():
            self.debug("IRC: process_queue thread says it's dead.")
            self.dead.clear()
            raise irclib.ServerNotConnectedError

      except irclib.ServerNotConnectedError:
        self.debug("IRC: Caught irclib.ServerNotConnectedError; restarting...")
        self.channels = []

  def queue_message(self, msg):
    self.debug("IRC: queue.put() %s" % msg)
    self.queue.put(msg)

  def process_queue(self):
    self.debug("IRC: Running (process_queue)!")

    while True:
      self.regulate_queue()

      self.debug("IRC: waiting on queue.get...")
      msg = self.queue.get()
      self.debug("IRC: queue.get() got %s" % msg)

      try:
        self.message_all(msg)
      except irclib.ServerNotConnectedError:
        self.debug("IRC: Got error when trying to send message. "
                   "Clearing channels")
        self.debug("IRC: process_queue() thread setting dead")
        self.channels = []
        self.dead.set()


  def regulate_queue(self):
    self.debug("IRC: Examining Queue...")

    size = self.queue.qsize()
    self.debug("IRC: Queue size = %i, queue_max = %i" \
               % (size, self.config.flood.queue_max))

    if size > self.config.flood.queue_max:
      items = 0

      self.debug("IRC: Queue - attempting to drop %i items" \
                 % self.config.flood.queue_drop)

      try:
        for i in range(0, self.config.flood.queue_drop):
          self.queue.get_nowait()
          items = items + 1
      except Queue.Empty:
        pass
 
      self.debug("IRC: Dropped %i of %i queued messages (flood)" \
                 % (items, size))
      self.message_all(action_message("dropped %i of %i queued messages "\
                                      "in the name of flood-control" % \
                                      (items, size)))

  def message_all(self, msg):
    self.debug("IRC: message() %s" % msg)

    for channel in self.channels:
      self.message(msg, channel)

  def message(self, msg, channel):
    with self.msglock as msglock:
      self.debug("IRC: message -> %s" % channel)
      self.connection.privmsg(channel, msg)

      self.debug("IRC: flood.wait...")
      time.sleep(self.config.flood.wait)
 
  def connect(self):
    self.debug("IRC: Connecting")

    s = self.config
    self.channels = []
    self.connection = self.irc.server()

    try:
      self.connection.connect(s.server, s.port, s.nick, s.password, s.user, \
                              s.realname)
    except irclib.ServerConnectionError:
      self.on_disconnect(self.connection, None)

    self.connection.add_global_handler("welcome", self.on_connect)
    self.connection.add_global_handler("join", self.on_join)
    self.connection.add_global_handler("disconncet", self.on_disconnect)

    for event in [ "kick", "part" ]:
      self.connection.add_global_handler(event, self.on_part);

  def on_connect(self, connection, event):
    if connection != self.connection:
      self.debug("IRC: Incorrect connection in on_connect")
      return

    self.debug("IRC: Connected; joining...")
    for channel in self.config.channels:
      self.connection.join(channel)

    self.reconnects = 0
 
  def on_join(self, connection, event):
    if connection != self.connection:
      self.debug("IRC: Incorrect connection in on_join")
      return

    self.debug("IRC: Joined channel %s" % event.target())

    if event.target() in self.channels:
      self.debug("IRC: Suppressed error: %s is already in self.channels" \
                 % event.target())
    else:
      self.config.join_msg(JoinMessageConnection(self, event.target()))
      self.channels.append(event.target())

  def on_disconnect(self, connection, event):
    if connection != self.connection:
      self.debug("IRC: Incorrect connection in on_disconnect")
      return

    self.channels = []
    self.reconnects += 1
    self.debug("IRC: Disconnected. self.reconnects = %i" % self.reconnects)

    proposed_wait = 2 ** self.reconnects
    if proposed_wait < self.config.max_reconnect_wait:
      self.debug("IRC: Sleeping for %i seconds" % proposed_wait)
      time.sleep(proposed_wait)
    else:
      self.debug("IRC: Sleeping for %i seconds (max)" \
          % self.config.max_reconnect_wait)
      time.sleep(self.config.max_reconnect_wait)

    self.debug("IRC: Slept; now raising irclib.ServerNotConnectedError " \
               "in order to reconnect...")
    raise irclib.ServerNotConnectedError

  def on_part(self, connection, event):
    if connection != self.connection:
      self.debug("IRC: Incorrect connection in on_part")
      return

    self.debug("IRC: Left %s" % event.target())
    try:
      self.channels.remove(event.target())
    except:
      self.debug("IRC: Suppressed error: couldn't remove %s from " \
                 "self.channels" % event.target())

class JoinMessageConnection():
  def __init__(self, bot, channel):
    self.bot = bot
    self.channel = channel

  def action(self, msg):
    self.message(action_message(msg))

  def message(self, msg):
    self.bot.debug("IRC: JoinMessageConnection message() %s" % msg)
    self.bot.message(msg, self.channel)

