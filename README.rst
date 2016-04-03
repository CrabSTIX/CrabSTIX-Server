==================================================================
CrabSTIX: Universal Syslog To STIX/TAXII Translator
==================================================================

STIX, TAXII, MAEC, CybOX will change the world. It's as simple as that. They provide the interchange format for us all to share threat information in realtime. The problem is that there aren't enough people producing intelligence in that format, or consuming it in a way that is useful for automated defense. 

This is where the CrabSTIX project comes in. This code base will aim to provide more useful translators and plumbing for the STIX/TAXII revolution. In short we want the world to be able to translate what ever they have in their security estate into actionable intelligence that can be shared with others.

CrabSTIX will start as a syslog to TAXII translator service for the IDS/IPS community, and with the help of your support, we will grow out to translate feeds from the majority of security devices and vendor families.

CrabSTIX creates a central aggregation point for syslog messages (just suricata currently). Messages sent to the CrabSTIX server are parsed into STIX format and sent via TAXII InboxMessages to a TAXII endpoint of your choosing.

Dependencies
------------
This project requires

    libtaxii
    python-stix
    netaddr

Usage
-----

To start the server simply run:

    >> python main.py ./crabstix.conf
