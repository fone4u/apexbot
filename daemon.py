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
import os
import threading
import traceback
import signal

# TODO: This is ugly. Do it like habitat, with a signal.alarm() fallback

class DaemonThread(threading.Thread):
  def __init__(self, log, **kwargs):
    super(DaemonThread, self).__init__(**kwargs)
    self.log = log
    self.daemon = True

  def run(self):
    try:
      super(DaemonThread, self).run()
    except:
      self.log.error("".join(traceback.format_exc()))
      self.log.info("DaemonThread: Attempting to kill process.")
      os.kill(os.getpid(), signal.SIGINT)

def immediate_death(a, b):
  sys.exit()

signal.signal(signal.SIGINT, immediate_death)

def wait():
  try:
    while True:
      signal.pause()
  except SystemExit:
    pass
