#!/usr/bin/python
#_________              ___.     ____________________._______  ___
#\_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /
#/    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     / 
#\     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \ 
# \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\  \
#        \/            \/    \/        \/                      \_/
# Name	 :	log_manager.py
# Function :	Log Manager
# Called By:	server.py

#Internal Modules
from config import Reader

#External modules
import logging
import datetime
import time
import sys
import os 

# Sockets
from socket import gethostname

class Logging:

	__single = None

	def __init__(self,argument_config):

		try:
			#Setup
			self._config = argument_config
			
			self._logging_level = int(self._config["LOGGING"]["log_level"])
			
			self._daemon_mode = self._config["LOGGING"]["daemon_mode"]

			# TODO: Error Handling Here
			if not os.path.exists(self._config["LOGGING"]["directory"]):
				os.makedirs(self._config["LOGGING"]["directory"])

			if not os.path.isfile(self._config["LOGGING"]["directory"]+"/crabstix.log"):

				open(self._config["LOGGING"]["directory"]+"/crabstix.log","w").close()


			if self._logging_level == 1:

				logging.basicConfig(format='%(asctime)s %(message)s',
									filename=self._config["LOGGING"]["directory"]+"/crabstix.log",
									level=logging.CRITICAL)

			elif self._logging_level == 2:

				logging.basicConfig(format='%(asctime)s %(message)s',
									filename=self._config["LOGGING"]["directory"]+"/crabstix.log",
									level=logging.ERROR)

			elif self._logging_level == 3:

				logging.basicConfig(format='%(asctime)s %(message)s',
									filename=self._config["LOGGING"]["directory"]+"/crabstix.log",
									level=logging.WARNING)

			elif self._logging_level == 4:

				logging.basicConfig(format='%(asctime)s %(message)s',
									filename=self._config["LOGGING"]["directory"]+"/crabstix.log",
									level=logging.INFO)

			elif self._logging_level == 5:

				logging.basicConfig(format='%(asctime)s %(message)s',
									filename=self._config["LOGGING"]["directory"]+"/crabstix.log",
									level=logging.DEBUG)
			
			else:
				print "There is an incorrect logging level in the crabstix.conf file"
				sys.exit()


			if self._daemon_mode == "False":

				print "\n"
				print "_________              ___.     ____________________._______  ___"
				print "\_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /"
				print "/    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     / "
				print "\     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \ "
				print " \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\ \\"
				print "        \/            \/    \/        \/                      \_/"
				print "                 - Let's connect the world! -"
				print "\n"

		except Exception, e:

			print "There was an error configuring the logging object " + str(e) + " : " + str(sys.exc_info())
			sys.exit()

	@classmethod
	def get_instance(cls,a):

		# One first run runs __init__
		# Subsequent requests just return an instance

		if not cls.__single:

			cls.__single = Logging(a)

		return cls.__single

	def critical(self, argument_message, argument_source, argument_type):

		message = "host=\"%s\" level=\"%s\" source=\"%s\" type=\"%s\" message=\"%s\"" % (gethostname(),
																						 "critical",
																						 argument_source,
																						 argument_type,
																						 argument_message)
		logging.critical(message)
		if self._daemon_mode != "Enabled":
			print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))+" : "+str(message)

	def error(self, argument_message, argument_source, argument_type):
		message = "host=\"%s\" level=\"%s\" source=\"%s\" type=\"%s\" message=\"%s\"" % (gethostname(),
																						 "error",
																						 argument_source,
																						 argument_type,
																						 argument_message)
		logging.error(message)
		if self._daemon_mode != "Enabled" and self._logging_level >= 2:
			print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))+" : "+str(message)

	def warning(self, argument_message, argument_source, argument_type):
		message = "host=\"%s\" level=\"%s\" source=\"%s\" type=\"%s\" message=\"%s\"" % (gethostname(),
																						 "warning",
																						 argument_source,
																						 argument_type,
																						 argument_message)
		logging.warning(message)
		if self._daemon_mode != "Enabled" and self._logging_level >= 3:
			print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))+" : "+str(message)

	def info(self, argument_message, argument_source, argument_type):
		message = "host=\"%s\" level=\"%s\" source=\"%s\" type=\"%s\" message=\"%s\"" % (gethostname(),
																						 "info",
																						 argument_source,
																						 argument_type,
																						 argument_message)
		logging.info(message)
		if self._daemon_mode != "Enabled" and self._logging_level >= 4:
			print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))+" : "+str(message)

	def debug(self, argument_message, argument_source, argument_type):
		message = "host=\"%s\" level=\"%s\" source=\"%s\" type=\"%s\" message=\"%s\"" % (gethostname(),
																						 "debug",
																						 argument_source,
																						 argument_type,
																						 argument_message)
		logging.debug(message)
		if self._daemon_mode != "Enabled" and self._logging_level == 5:
			print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))+" : "+str(message)
		
	#### Custom Cases ####
	def stix(self, argument_stix_message):

		with open(self._config["LOGGING"]["directory"]+"/stix.log","a") as f:
			f.write(argument_stix_message)

	def unparsable(self, argument_log_line):
		with open(self._config["LOGGING"]["directory"]+"/unparsable.log","a") as f:
			f.write(argument_log_line)