#!/usr/bin/env python2
# Copyright © 2011 Thomas Schreiber <ubiquill@gmail.com>
#
# upgrade.py
#
# Installs and upgrades packages


import sys
import os
import json

from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.python.util import println

class UpgradeAUR:

    def __init__(self, target):
        self.downloadPkgbuild(target)


    def downloadPkgbuild(self, target):
        self.getPkgInfo(target)
        self.getPkgbuild(target)
        self.getSource(target)

    def getPkgInfo(self, target):
        AURURL = 'http://aur.archlinux.org/rpc.php?type=info&arg='
        self.info = []
        infoURL = AURURL + target

        getPage(infoURL).addCallbacks(
            callback=lambda value:(self.decodeResponse(value), reactor.stop()),
            errback=lambda error:(println("an error occured",error),reactor.stop()))

        reactor.run()

    def decodeResponse(self, value):
        print value
        #jsonValue = json.loads(value)
        #self.info = jsonValue['results']


    def getPkgbuild(self, target):
        # Download pkgbuild
        pass


    def getSource(self, target):
        # Download source
        pass


    
if __name__ == '__main__':
    upgrade = UpgradeAUR(sys.argv[1])
