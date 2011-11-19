# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This file Copyright Jon Sowman 2011 (jon@hexoc.com)

import sys
import os
from datetime import datetime

class ChannelLogger:
    """Log events in an IRC channel to a logfile"""

    def __init__(self, config, log):
        """
        Construct the ChannelLogger, allowing log and config to be
        accessed from inside the class
        """

        self.config = config
        self.log = log

    def log_event(self, c, e):
        """
        Given instances of a Connection, and an Event, fully handle
        interpreting the event and writing it to the logfile.
        """

        messages = [ 'pubmsg', 'pubnotice' ]
        actions = [ 'join', 'quit', 'part', 'kick' ]
        ctcp = [ 'ctcp' ]
        logstr = ""

        # Determine whether the event was a msg/notice, or a join/part/quit
        if (e.eventtype() in messages):
          # Extract the username from which the message came
          user = e.source().rsplit('!')[0]
          msg = e.arguments()[0]
          logstr = "<%s> %s" % (user, msg)
        elif (e.eventtype() in actions):
          logstr = "-!- %s" % self.__parse_action(e)
        elif (e.eventtype() in ctcp and e.arguments()[0] == "ACTION"):
          user = e.source().rsplit('!')[0]
          print e.arguments()
          msg = str(e.arguments()[1])
          logstr = " * %s %s" % (user, msg)
        else:
          self.log.info("ChannelLogger: Unhandled IRC event: '%s'" 
                  % e.eventtype())
          return False

        # Prepend the timestamp to the string
        logstr = self.__prepend_timestamp(logstr)

        # Write the string to the log
        try:
            logfile = e.target().rsplit("#")[1] + ".log"
        except:
            self.log.info("ChannelLogger: Suppressed error - no event \
                    target")
            logfile = "None"
        if (self.__write_log(logstr, logfile)):
            return True
        else:
            self.log.debug("ChannelLogger: Failed to write to the \
                    log file")
            return False

    def __parse_action(self, event):
        """
        For an action, as defined in log_event(), construct a suitable
        entry for the logfile such that it matches the format
        used by irssi.
        """

        user = event.source().rsplit('!')[0]
        host = event.source().rsplit('!')[1]
        channel = event.target()
        action = event.eventtype().upper()
        action_string = ""
        if (action == 'JOIN'):
            action_string = "%s [%s] has joined %s" % (user, host, channel)
        elif (action == 'QUIT'):
            action_string = "%s [%s] has quit [%s]" % \
                (user, host, event.arguments()[0])
        elif (action == 'PART'):
            action_string = "%s [%s] has parted %s" % (user, host, channel)
        elif (action == 'KICK'):
            action_string = "%s [%s] was kicked from %s" % \
                (user, host, channel)
        else:
            action_string = "%s [%s] triggered event %s in %s" % \
                (user, host, action, channel)
        return action_string

    def __prepend_timestamp(self, log_string):
        """
        Prepend a proper date and time stamp to the log entry to
        prepare it for writing to the log file.
        Should match the irssi logging format.
        """

        # Prepend the timestamp to the log entry
        d = datetime.now()
        stamp = d.strftime("%Y-%m-%d %H:%M:%S")
        logstr = "%s %s" % (stamp, log_string)
        return logstr

    def __write_log(self, log_string, logfile):
        """
        Write the supplied string to the logfile.
        """

        if (logfile == "None" or logfile == ""):
            self.log.info("ChannelLogger: Tried to write to a non-file")
            return False

        if (log_string == ""):
            self.log.info("ChannelLogger: Tried to write nothing to log")
            return False

        self.log.info("ChannelLogger: %s" % log_string)

        # Get the logging directory from config and check if it exists.
        # If not, create it.
        logdir = self.config.logdir
        if not (os.path.isdir(logdir)):
            os.makedirs(logdir)

        # Generate the name of the file to which to log.
        logfile = os.path.join(logdir, logfile)

        # Open the file, write the log line, and close the file.
        file_handle = open(logfile, "a")
        file_handle.write(log_string + "\n")
        file_handle.close()

        return True
