#!/usr/bin/env python2
# Thomas Schreiber 2011 <ubiquill@gmail.com>

# aur.py
#
# A collection of functions to help search the AUR

import sys
import json

from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.python.util import println

if (__name__ == "__main__"):
  

    if (len(sys.argv) <= 1):
        sys.exit()
    else:
        argument = sys.argv[1]

    queryUrl = 'http://aur.archlinux.org/rpc.php?type=search&arg=' 
    queryUrl += argument

    getPage(queryUrl).addCallbacks(
        callback=lambda value:(println(value),reactor.stop()),
        errback=lambda error:(println("an error occured",error),reactor.stop()))

    reactor.run()
