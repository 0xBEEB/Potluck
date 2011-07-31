#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

# query.py
# by Thomas Schreiber <ubiquill@gmail.com>
#
# Query the repositories and AUR

import sys
import os
import json
import urllib.request, urllib.parse, urllib.error
import stat
import subprocess

AURURL = 'http://aur.archlinux.org'

class Query:
    """Searches the AUR using the scripting API"""


    def __init__(self, term):
        """Initializes an AUR query.
        :param term: key phrase to search for.
        """
        self.AURURL = 'http://aur.archlinux.org/rpc.php?type=search&arg='
        self.query = []
        self.search(term)


    def search(self, term):
        """Search fhe AUR.
        :param term: keyword to search for.
        """
        queryURL = self.AURURL + term
        value = urllib.request.urlopen(queryURL).read()
        self.decodeResponse(value.decode("utf-8"))
        

    def decodeResponse(self, value):
        """Decodes JSON from AUR query.
        :param value: raw JSON input.
        """
        jsonValue = json.loads(value)
        self.query = jsonValue['results']


    def printQuery(self):
        """Print the reslut of the Query to stdout.
        """
        for app in self.query:
            print('aur/' + app['Name'] + ' ' + app['Version'])
            print('    ' + app['Description'])
        #print jsonValue['results']




class Upgrade:
    """Upgade class used to hold information about AUR upgrade.
    """


    def __init__(self, target):
        """Initializes an upgrade object
        :param target: Application to upgrade.
        """
        self.target = target
        self.downloadPkgbuild()
        self.buildDepends = self.getBuildDepends()
        self.depends = self.getDepends()


    def downloadPkgbuild(self):
        """Downloads the PKGBUILD associated with a package.
        """
        self.AURURL = 'http://aur.archlinux.org'
        self.getPkgInfo()
        self.getPkgbuild()


    def getPkgInfo(self):
        """Gets information about a package.
        """
        AURSearchURL = self.AURURL + '/rpc.php?type=info&arg='
        self.info = []
        infoURL = AURSearchURL + self.target

        value = urllib.request.urlopen(infoURL).read()
        self.decodeResponse(value.decode("utf-8"))


    def decodeResponse(self, value):
        """Decodes JSON response from AUR.
        """
        self.info = json.loads(value)
        response = self.info['results']
        self.pkgURL = self.AURURL + response['URLPath']


    def getPkgbuild(self):
        """Downloads PKGBUILD file.
        """
        pkgbuildURL = self.AURURL + '/packages/' + self.target + '/PKGBUILD'
        urllib.request.urlretrieve(pkgbuildURL, self.target + '.PKGBUILD')


    def getDepends(self):
        """Creates a list of the packages dependency.
        """
        retCode = subprocess.call(["chmod", "+x", self.target + ".PKGBUILD"])
        dependsString = subprocess.check_output(["./model/getDepends.sh", self.target])
        dependsString = dependsString.decode("utf-8")
        depends = list(dependsString.split())
        return depends


    def getBuildDepends(self):
        """Creates a list of the packages build dependencies.
        """
        retCode = subprocess.call(["chmod", "+x", self.target + ".PKGBUILD"])
        dependsString = subprocess.check_output(["./model/getBuildDepends.sh", self.target])
        dependsString = dependsString.decode("utf-8")
        buildDepends = list(dependsString.split())
        return buildDepends


    def makePkg(self):
        """Creates package from PKGBUILD.
        """
        try:
             retCode = subprocess.call('makepkg -s PKGBUILD')
             return retCode
        except:
             pass



def outOfDate():
    """Checks AUR packages to see if they are out of date.
    """
    resultList = []
    updateList = []
    response = {}
    extensiveResponse = {}
    output = subprocess.check_output(["pacman", "-Qm"])
    output = output.decode("utf-8")
    tempList = output.splitlines()
    for app in tempList:
        temp = app.split(' ')
        resultList.append(temp)

    for app in resultList:
        response = getPkgInfo(app[0])
        if isinstance(response, dict):
            if response['OutOfDate'] != 0:
                isNew = subprocess.check_output(["vercmp", response['Version'], app[1]])
                isNew = isNew.decode("utf-8")
                value = isNew.splitlines()
                if int(value[0]) > 0:
                    response['repo'] = 'aur'
                    updateList.append(response)
    return updateList


def getPkgInfo(target):
    """Gather info about the target package.
    :param target: Application for which to ather information about.
    """
    AURSearchURL = AURURL + '/rpc.php?type=info&arg='
    info = []
    infoURL = AURSearchURL + target

    value = urllib.request.urlopen(infoURL).read()
    info = json.loads(value.decode("utf-8"))
    response = info['results']
    return response




# This is for unit testing
if (__name__ == "__main__"):
  
    if (len(sys.argv) <= 1):
        sys.exit()
    else:
        argument = sys.argv[1]
 
    os.system('/usr/bin/pacman -Ss ' + argument)

    query = QueryAUR(argument)
    query.printQuery()




# vim: set ts=4 sw=4 noet:
