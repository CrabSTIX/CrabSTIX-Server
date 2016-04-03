#!/usr/bin/python
#_________				  ___.	  ____________________._______  ___
#\_	___ \____________ \_ |__  /	_____/\__	 ___/|	\	\/  /
#/	 \  \/\_  __ \__  \ | __ \ \_____  \	|	 |	|	|\	  / 
#\	  \____|  | \// __ \| \_\ \/		  \  |	 |	|	|/	  \ 
# \______  /|__|  (____  /___  /_______  /  |____|	|___/___/\  \
#		  \/				\/	 \/		  \/							 \_/
# Name	  :	suricata.py
# Function :	Suricata parser
# Called By:	server.py

import re
import time
import datetime

# STIX 
from stix.core import STIXPackage, STIXHeader
from stix.incident import Incident,Time
from cybox.core import Observable 
from cybox.objects.address_object import Address

# netaddr
from netaddr import IPAddress

class Parser:
	"""

	Identified on the format of a Suricata IDS log and parses syslog line to STIX/CybOX incidents

	"""
	def __init__(self):

		self._name = __name__

		self._regex = {}
		self._regex["time"] = "^(.*?)(\.\d+)?\s+"
		self._regex["sid"] = ".*\[\*\*\]\s+\[\d+\:(\d+)\:"
		self._regex["text"] = ".*\:\d+\]\s+(.*?)\s+\[\*\*\]"
		self._regex["classification"] = ".*\[Classification\:\s+(.*?)\]\s+"
		self._regex["priority"] = ".*\[Priority\:\s+(\d+)\]\s+"
		self._regex["source_ip"] = ".*\}\s+(.*?)\:\d+\s+\-\>"
		self._regex["source_port"] = ".*\}\s+.*\:(\d+)\s+\-\>"
		self._regex["destination_ip"] = ".*\s+\-\>\s+(.*?)\:\d"
		self._regex["destination_port"] = ".*\s+\-\>.*\:(\d+)"

	def identify(self,argument_log):

		"""
		Identifies suricata log messages.

		:param argument_log: The log line to try and identify
		:return: True if the log is a valid Suricata IDS log
			
		"""
		pattern = re.compile("^\d+\/\d+\/\d+\-\d+\:\d+\:\d+\.\d+\s+\[\*\*\]\s+\[\d+\:\d+\:\d+\]\s+.*?\[\*\*\]\s+\[")

		if pattern.match(argument_log):

			return True

		else:

			return False


	def parse(self, argument_log):

		"""
		Parses Suricata IDS log lines into STIX/CybOX format.

		:param argument_log: The log line to try and identify
		:return: STIX Incident 
			
		"""
		parsed_suricata_log = {}

		for regex in self._regex:

			try:
				parsed_suricata_log[regex] = re.match(self._regex[regex], argument_log).group(1)
			except:
				print "Failed to parse %s" % (regex)
				return False

		#TODO: Time Zones
		parsed_suricata_log["unix_timestamp"] = time.mktime(datetime.datetime.strptime(parsed_suricata_log["time"], "%m/%d/%Y-%M:%H:%S").timetuple())


		# Find IP's of interest
		if IPAddress(parsed_suricata_log["source_ip"]).is_private() == False or IPAddress(parsed_suricata_log["destination_ip"]).is_public() == False:

			stix_package = STIXPackage()

			# If the source is public
			if not IPAddress(parsed_suricata_log["source_ip"]).is_private() and IPAddress(parsed_suricata_log["destination_ip"]).is_private():

				incident = Incident(title="[IDS Alert] "+parsed_suricata_log["text"]+" From "+ parsed_suricata_log["source_ip"])
				addr = Address(address_value=parsed_suricata_log["source_ip"], category=Address.CAT_IPV4)

			elif IPAddress(parsed_suricata_log["source_ip"]).is_private() and not IPAddress(parsed_suricata_log["destination_ip"]).is_private():

				incident = Incident(title="[IDS Alert] "+parsed_suricata_log["text"]+" To "+ parsed_suricata_log["destination_ip"])
				addr = Address(address_value=parsed_suricata_log["destination_ip"], category=Address.CAT_IPV4)
			
			else:

				#public to public - i can't tell who the bad guy is
				return False

			incident.time = Time()
			incident.time.first_malicious_action = parsed_suricata_log["time"]
			observable = Observable(item=addr)
			stix_package.add_observable(observable)
			stix_package.add_incident(incident)

		return stix_package.to_xml()