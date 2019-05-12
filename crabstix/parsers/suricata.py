#!/usr/bin/python
# _________              ___.     ____________________._______  ___
# \_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /
# /    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     /
# \     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \
#  \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\  \
#        \/            \/    \/        \/                      \_/
# Name      :    suricata.py
# Function :    Suricata parser
# Called By:    server.py

import re
import time
import datetime

# STIX
from stix.core import STIXPackage
from stix.incident import Incident, Time
from stix.common.related import RelatedObservable

# Namespace fun
from cybox.utils.nsparser import Namespace
import stix.utils

from cybox.core import Observable
from cybox.objects.address_object import Address

# netaddr
from netaddr import IPAddress


class Parser:
    """
    Identified on the format of a Suricata IDS log and parses
    syslog line to STIX/CybOX incidents
    """
    def __init__(self, argument_config):

        self._name = __name__

        self._config = argument_config

        self._regex = {}
        self._regex["time"] = "^(.*?)(\.\d+)?\s+" # noqa W605
        self._regex["sid"] = ".*\[\*\*\]\s+\[\d+\:(\d+)\:" # noqa W605
        self._regex["text"] = ".*\:\d+\]\s+(.*?)\s+\[\*\*\]" # noqa W605 
        self._regex["classification"] = ".*\[Classification\:\s+(.*?)\]\s+" # noqa W605 
        self._regex["priority"] = ".*\[Priority\:\s+(\d+)\]\s+" # noqa W605 
        self._regex["source_ip"] = ".*\}\s+(.*?)\:\d+\s+\-\>" # noqa W605 
        self._regex["source_port"] = ".*\}\s+.*\:(\d+)\s+\-\>" # noqa W605 
        self._regex["destination_ip"] = ".*\s+\-\>\s+(.*?)\:\d" # noqa W605 
        self._regex["destination_port"] = ".*\s+\-\>.*\:(\d+)" # noqa W605 

    def identify(self, argument_log):

        """
        Identifies suricata log messages.

        :param argument_log: The log line to try and identify
        :return: True if the log is a valid Suricata IDS log
        """
        argument_log = " ".join(argument_log.split(" ")[5:])

        pattern = re.compile("^\d+\/\d+\/\d+\-\d+\:\d+\:\d+\.\d+\s+\[\*\*\]\s+\[\d+\:\d+\:\d+\]\s+.*?\[\*\*\]\s+\[") # noqa W605, E501

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
        argument_log = " ".join(argument_log.split(" ")[5:])
        parsed_log = {}

        for regex in self._regex:
            try:
                parsed_log[regex] = re.match(
                    self._regex[regex], argument_log).group(1)
            except: # noqa E722
                print "Failed to parse %s" % (regex)
                return False

        # TODO: Time Zones
        parsed_log["unix_timestamp"] = time.mktime(
            datetime.datetime.strptime(
                parsed_log["time"],
                "%m/%d/%Y-%H:%M:%S").timetuple())

        # Find IP's of interest
        source_ispriv = IPAddress(parsed_log["source_ip"]).is_private()
        dest_ispriv = IPAddress(parsed_log["destination_ip"]).is_private()

        if source_ispriv is False or dest_ispriv is False:

            # Name Space
            stix.utils.idgen.set_id_namespace(
                Namespace(
                    self._config["NAMESPACE"]["url"],
                    self._config["NAMESPACE"]["name"], ""))

            stix_package = STIXPackage()

            # If the source is public
            if not source_ispriv and dest_ispriv:

                incident = Incident(title="[IDS Alert] {} From {}".format(
                    parsed_log["text"],
                    parsed_log["source_ip"]))

                addr = Address(
                    address_value=parsed_log["source_ip"],
                    category=Address.CAT_IPV4)

            elif source_ispriv and not dest_ispriv:

                incident = Incident(
                    title="[IDS Alert] {} To {}".format(
                        parsed_log["text"],
                        parsed_log["destination_ip"]))

                addr = Address(
                    address_value=parsed_log["destination_ip"],
                    category=Address.CAT_IPV4)

            else:
                # public to public - i can't tell who the bad guy is
                return False

            observable = Observable(
                item=addr,
                title="[IP Associated To IDS Alert] "+parsed_log["text"],
                description="""
    This ip address was seen to be involved in triggering the IDS
    alert %s if seen from multiple sources, this is a good
    indicator of a potential threat actor or compromised host""" % (
                    parsed_log["text"]))
            stix_package.add_observable(observable)

            incident.time = Time()
            incident.time.first_malicious_action = parsed_log["time"]

            related_obs = RelatedObservable(Observable(idref=observable.id_))
            incident.related_observables.append(related_obs)

            stix_package.add_incident(incident)

        return stix_package.to_xml()
