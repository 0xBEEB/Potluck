#!/usr/bin/env python2
# coding=UTF-8

# Copyright © 2011 Thomas Schreiber
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# upgrade.py
# by Thomas Schreiber <ubiquill@gmail.com>
#
# Installs and upgrades packages


import sys
import os
import json
import urllib

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
        pkgbuildURL = 'http://aur.archlinux.org/packages/' + target + '/PKGBUILD'
        urllib.urlretrieve(pkgbuildURL, '/home/ubiquill/PKGBUILD')


    def getSource(self, target):
        # Download source
        pass


    
if __name__ == '__main__':
    upgrade = UpgradeAUR(sys.argv[1])
