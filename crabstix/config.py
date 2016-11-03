#!/usr/bin/python
#_________              ___.     ____________________._______  ___
#\_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /
#/    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     / 
#\     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \ 
# \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\  \
#        \/            \/    \/        \/                      \_/
# Name	 :	config.py
# Function :	Config reader
# Called By:	server.py

from ConfigParser import SafeConfigParser

class Reader():

	"""
	Wrapper for SafeConfigParser. Converts config file into a dict
	"""
	__single = None

	def __init__(self):

		self._parser = SafeConfigParser()
		self._parser.optionxform = str
		self._config = ""

	@classmethod
	def get_instance(cls):

		# One first run runs __init__
		# Subsequent requests just return an instance

		if not cls.__single:

			cls.__single = Reader()

		return cls.__single

	def get_config(self, arugment_config_file):
		"""
		Identifies suricata log messages.

		:param argument_config_file: The path to the crabstix.conf file
		:return: dictionary of configuration variables
			
		"""

		# Read first time
		if self._config == "":

			self._config = {}
			
			#Read in the config file
			self._parser.read(arugment_config_file)

			#Split it into sections
			sections = self._parser.sections()

			#Read by section
			for section in sections:

				#Temp dict
				option_dict = {}

				#Read all the options for this section
				options = self._parser.options(section)

				#For each option get the value
				for option in options:

					option_dict[option] = self._parser.get(section, option)

				#Add it to the global config object
				self._config[section] = option_dict

			# Parse Destinations
			for dest in self._config["DESTINATIONS"]:

				destination_split = self._config["DESTINATIONS"][dest].split(",")
				
				self._config["DESTINATIONS"][dest] = {}
				self._config["DESTINATIONS"][dest]["target"] = destination_split[0]
				self._config["DESTINATIONS"][dest]["port"] = destination_split[1]
				self._config["DESTINATIONS"][dest]["inbox_endpoint"] = destination_split[2]
				self._config["DESTINATIONS"][dest]["collection_name"] = destination_split[3]
				self._config["DESTINATIONS"][dest]["auth_type"] = destination_split[4]

				if len(destination_split) > 5: 
					self._config["DESTINATIONS"][dest]["username"] = destination_split[5]
					self._config["DESTINATIONS"][dest]["password"] = destination_split[6]

			return self._config

		else:

			return self._config