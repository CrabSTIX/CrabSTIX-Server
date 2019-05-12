#!/usr/bin/python
# _________              ___.     ____________________._______  ___
# \_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /
# /    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     /
# \     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \
#  \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\  \
#        \/            \/    \/        \/                      \_/
# Name     :    config.py
# Function :    Config reader
# Called By:    server.py

# External modules
import logging
import datetime
import sys
import os

# Sockets
from socket import gethostname


class Logging:

    __single = None

    def __init__(self, argument_config):

        try:
            # Setup
            self._config = argument_config
            self._logging_level = int(self._config["LOGGING"]["log_level"])
            self._daemon_mode = self._config["LOGGING"]["daemon_mode"]
            self._log_template = "host=\"%s\" level=\"%s\" source=\"%s\" type=\"%s\" message=\"%s\"" # noqa E501

            # TODO: Error Handling Here
            if not os.path.exists(self._config["LOGGING"]["directory"]):
                os.makedirs(self._config["LOGGING"]["directory"])

            log_file = self._config["LOGGING"]["directory"]+"/crabstix.log"
            if not os.path.isfile(log_file): # noqa E501
                open(log_file, "w").close()

            if self._logging_level == 1:
                logging.basicConfig(
                    format='%(asctime)s %(message)s',
                    filename=log_file,
                    level=logging.CRITICAL)

            elif self._logging_level == 2:
                logging.basicConfig(format='%(asctime)s %(message)s',
                                    filename=log_file,
                                    level=logging.ERROR)

            elif self._logging_level == 3:
                logging.basicConfig(format='%(asctime)s %(message)s',
                                    filename=log_file,
                                    level=logging.WARNING)

            elif self._logging_level == 4:
                logging.basicConfig(format='%(asctime)s %(message)s',
                                    filename=log_file,
                                    level=logging.INFO)

            elif self._logging_level == 5:
                logging.basicConfig(format='%(asctime)s %(message)s',
                                    filename=log_file,
                                    level=logging.DEBUG)
            else:
                print "Incorrect logging level in the crabstix.conf file"
                sys.exit()

            if self._daemon_mode == "False":
                print "\n"
                print "_________              ___.     ____________________._______  ___" # noqa E501
                print "\_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /" # noqa E501
                print "/    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     / " # noqa E501
                print "\     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \ " # noqa E501
                print " \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\ \\" # noqa E501
                print "        \/            \/    \/        \/                      \_/" # noqa E501
                print "                 - Let's connect the world! -"
                print "\n"

        except Exception, e:

            print "Error configuring the logging object: %s : %s" % (
                str(e), str(sys.exc_info()))
            sys.exit()

    @classmethod
    def get_instance(cls, a):

        # One first run runs __init__
        # Subsequent requests just return an instance

        if not cls.__single:
            cls.__single = Logging(a)

        return cls.__single

    def critical(self, argument_message, argument_source, argument_type):
        message = self._log_template % (gethostname(),
                                        "critical",
                                        argument_source,
                                        argument_type,
                                        argument_message)
        logging.critical(message)

        if self._daemon_mode != "Enabled":
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print str(timestamp+" : "+str(message))

    def error(self, argument_message, argument_source, argument_type):
        message = self._log_template % (gethostname(),
                                        "error",
                                        argument_source,
                                        argument_type,
                                        argument_message)
        logging.error(message)

        if self._daemon_mode != "Enabled":
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print str(timestamp+" : "+str(message))

    def warning(self, argument_message, argument_source, argument_type):
        message = self._log_template % (gethostname(),
                                        "warning",
                                        argument_source,
                                        argument_type,
                                        argument_message)
        logging.warning(message)

        if self._daemon_mode != "Enabled":
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print str(timestamp+" : "+str(message))

    def info(self, argument_message, argument_source, argument_type):
        message = self._log_template % (gethostname(),
                                        "info",
                                        argument_source,
                                        argument_type,
                                        argument_message)
        logging.info(message)
        if self._daemon_mode != "Enabled":
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print str(timestamp+" : "+str(message))

    def debug(self, argument_message, argument_source, argument_type):
        message = self._log_template % (gethostname(),
                                        "debug",
                                        argument_source,
                                        argument_type,
                                        argument_message)
        logging.debug(message)

        if self._daemon_mode != "Enabled":
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print str(timestamp+" : "+str(message))

    # Custom Cases #
    def stix(self, argument_stix_message):
        stix_log = self._config["LOGGING"]["directory"]+"/stix.log"
        with open(stix_log, "a") as f:
            f.write(argument_stix_message)

    def unparsable(self, argument_log_line):
        unparse_log = self._config["LOGGING"]["directory"]+"/unparsable.log"
        with open(unparse_log, "a") as f:
            f.write(argument_log_line)
