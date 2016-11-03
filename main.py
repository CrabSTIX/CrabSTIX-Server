#!/usr/bin/python
#_________              ___.     ____________________._______  ___
#\_   ___ \____________ \_ |__  /   _____/\__    ___/|   \   \/  /
#/    \  \/\_  __ \__  \ | __ \ \_____  \   |    |   |   |\     / 
#\     \____|  | \// __ \| \_\ \/        \  |    |   |   |/     \ 
# \______  /|__|  (____  /___  /_______  /  |____|   |___/___/\  \
#        \/            \/    \/        \/                      \_/
# Name     :	main.py
# Function :	Start the program
# Called By:	User / OS
"""
All main.py is responsible for is checking the user supplied config file exists, and starting the server.

Once started main.py handles the servers exit conditions.
"""
import sys
import os
import threading
from crabstix import server


def signal_handler(signum, frame):

	print "Exiting"

if __name__ == "__main__":

	if len(sys.argv) > 1:
		
		if os.path.isfile(sys.argv[1]):

			try:
				
				server = server.CrabSTIXServer(server.LogHandler,sys.argv[1])
				t = threading.Thread(target=server.serve_forever(poll_interval=0.5))
				t.setDaemon(True)
				t.start()

				# Wait for end
				signal.signal(signal.SIGINT, signal_handler)
				signal.pause()
			
			except KeyboardInterrupt:
			
				pass
		
		else:

			print "Error: %s not found" % (sys.argv[1])
	else:

		print "\n  Usage: ./main.py crabstix.conf\n"