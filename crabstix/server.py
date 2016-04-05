#!/usr/bin/python
#_________              ___.     ____________________._______  ___
#\_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /
#/    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     / 
#\     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \ 
# \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\  \
#        \/            \/    \/        \/                      \_/
# Name     :	server.py
# Function :	Listen to a user supplied port, pass logs to relevant parsers
# Called By:	main.py

# Python
import os
import SocketServer
import urllib2

# Local
from log_manager import Logging
from config import Reader
import crabstix.parsers

#TAXII

import libtaxii as t
import libtaxii.messages_11 as tm11
import libtaxii.clients as tc
from libtaxii.common import generate_message_id
from libtaxii.constants import *
from dateutil.tz import tzutc

class CrabSTIXServer(SocketServer.ThreadingTCPServer):

	"""
	Listens on a user supplied port and forwards the messages to the matching parser
	"""

	def __init__(self, RequestHandlerClass, ConfigPath):

		"""
		Overrides the SocketServer __init__ to add out conf and parser modules
		Doing this allows them to be called by the handler.

		To stop the config reader needing to be definined first, this module loads
		the config reader in the __init__ method and passes the host and port
		while initialising.

		:param server_address: (HOST,PORT) - These are read from the config file
		:param RequestHandlerClass: Handler class (see LogHandler)
		:param ConfigPath: The path to our crabstix.conf
		"""
		self._config = Reader().get_config(ConfigPath)
		self._logging = Logging.get_instance(self._config)


		# Load all the parsers
		self._parsers = {}


		for module in os.listdir("./crabstix/parsers"):

			if module.endswith(".py") and module != "__init__.py":

				# Import the module, load the Parser class, store in a dict by parser name
				self._parsers[module[:-3]] = (getattr(getattr(crabstix.parsers, module[:-3]),"Parser")(self._config))
				self._logging.info("Loaded parser %s" % (module[:-3]),
								   "server.py",
								   "informational")

		# Start the server
		SocketServer.ThreadingTCPServer.__init__(self,
												(self._config["SERVER"]["host"],int(self._config["SERVER"]["port"])),
												RequestHandlerClass)
		self._logging.info("Server started on %s:%s" % (self._config["SERVER"]["host"],int(self._config["SERVER"]["port"])),
								   "server.py",
								   "informational")

class LogHandler(SocketServer.BaseRequestHandler):

	"""
	Accepts TCP connections from Syslog, reads 1k chunks and passes them to the parser
	On a successful parse, the STIX XML is passed of to the TAXII api specified in crabstix.conf
	"""

	def handle(self):

		"""
		Handles TCP connections
		"""
		while True:
			
			log_line = self.request.recv(1024) 
			if log_line != "":
				
				self.server._logging.debug("%s - %s" % (self.client_address[0], str(log_line.rstrip("\n"))),
									"server.py",
									"received_log")		
				
				identified_flag = False
				for parser in self.server._parsers:

					if self.server._parsers[parser].identify(log_line):

						# Mark as identified
						identified_flag = True

						# TODO: Log this to a file
						stix_log = self.server._parsers[parser].parse(log_line)

						if stix_log:

							# Stix parsed correctly

							# Write to file
							self.server._logging.stix(stix_log)

							# If TAXII is enabled - send to taxii
							if self.server._config["TAXII"]["enabled"]:

								#InProgress: Send to TAXII - http://libtaxii.readthedocs.org/en/stable/api/clients.html
								# 						   - http://libtaxii.readthedocs.org/en/stable/api/messages_11.html#inbox-message
								#					 	   - https://github.com/TAXIIProject/libtaxii/blob/master/libtaxii/scripts/inbox_client.py

								# Make a client

								# TODO: Handle https
								client = tc.HttpClient()
								

								if self.server._config["TAXII"]["authentication"] == "NONE":

									client.set_auth_type(tc.HttpClient.AUTH_NONE)
									client.set_use_https(False)

								elif self.server._config["TAXII"]["authentication"] == "BASIC":

									client.set_auth_type(tc.HttpClient.AUTH_BASIC)
									client.set_auth_credentials({'username': self.server._config["TAXII"]["username"],
																 'password': self.server._config["TAXII"]["password"]})

								else:

									self.server._logging.error("Failed to send message to TAXII endpoint: Invalid HTTP AUTH",
															   "server.py",
															   "taxii_error")
									break

								# Build a content block CB_STIX_XML_111"
								cb = tm11.ContentBlock(tm11.ContentBinding(CB_STIX_XML_111), stix_log)

								# Built the full XML body
								inbox_message = tm11.InboxMessage(message_id=tm11.generate_message_id(),content_blocks=[cb])

								# Add dcns
								if self.server._config["TAXII"]["inbox_dcn"]:
									inbox_message.destination_collection_names.append(self.server._config["TAXII"]["inbox_dcn"])

								inbox_xml = inbox_message.to_xml(pretty_print=True)
								print inbox_xml
								try:

									# Send to TAXII endpoint
									http_resp = client.call_taxii_service2(self.server._config["TAXII"]["hostname"],
																		   self.server._config["TAXII"]["inbox_endpoint"],
																		   VID_TAXII_XML_11, inbox_xml)

									taxii_message = t.get_message_from_http_response(http_resp, inbox_message.message_id)
								
								except urllib2.URLError:

									self.server._logging.error("Failed to send message to TAXII endpoint: URLError",
															   "server.py",
															   "taxii_error")

								else:
									# TODO: Parse for success
									print taxii_message.to_xml(pretty_print=True)

						else:

							self.server._logging.error("%s parser failed to parse a message, it will be added to the unparsable log." % (parser),
												"server.py",
												"parse_error")

							self.server._logging.unparsable(log_line)


				# Check if parsed
				if not identified_flag:

					self.server._logging.error("No matching parsers were found for a log, it will be added to the unparsable log.",
										"server.py",
										"parse_error")

					self.server._logging.unparsable(log_line)

			else:
				
				# The connection has ended
				break	