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

import os
import SocketServer
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

		SocketServer.ThreadingTCPServer.__init__(self,
												(self._config["SERVER"]["host"],int(self._config["SERVER"]["port"])),
												RequestHandlerClass)

		# Load all the parsers
		self._parsers = {}


		for module in os.listdir("./crabstix/parsers"):

			if module.endswith(".py") and module != "__init__.py":

				# Import the module, load the Parser class, store in a dict by parser name
				self._parsers[module[:-3]] = (getattr(getattr(crabstix.parsers, module[:-3]),"Parser")())

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
				
				print( "%s : " % self.client_address[0], str(log_line))		
				
				parsed_flag = False
				for parser in self.server._parsers:

					if self.server._parsers[parser].identify(log_line):

						# TODO: Log this to a file
						stix_log = self.server._parsers[parser].parse(log_line)

						if stix_log:

							#TODO: Send to TAXII - http://libtaxii.readthedocs.org/en/stable/api/clients.html
							# 					 - http://libtaxii.readthedocs.org/en/stable/api/messages_11.html#inbox-message
							#					 - https://github.com/TAXIIProject/libtaxii/blob/master/libtaxii/scripts/inbox_client.py

							# Make a client
							client = tc.HttpClient()
							client.set_auth_type(tc.HttpClient.AUTH_NONE)
							client.set_use_https(False)

							# Build a content block
							cb = tm11.ContentBlock(tm11.ContentBinding("CB_STIX_XML_111"), stix_log)

							# Built the full XML body
							inbox_message = tm11.InboxMessage(message_id=tm11.generate_message_id(),content_blocks=[cb])
							inbox_xml = inbox_message.to_xml(pretty_print=True)
							# Send to taxitest
							http_resp = client.call_taxii_service2('taxiitest.mitre.org', '/services/inbox/', VID_TAXII_XML_11, inbox_xml)
							taxii_message = t.get_message_from_http_response(http_resp, inbox_message.message_id)
							print taxii_message.to_xml(pretty_print=True)

						parsed_flag = True

				# Check if parsed
				if not parsed_flag:

					print "No matching parsers were available for this log"

			else:
				
				# The connection has ended
				break