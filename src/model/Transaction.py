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

# Potluck
# by Thomas Schreiber <ubiquill@gmail.com>

# TODO: Uporn completion of pyalpm much of this will need to be rewritten

from PyQt4.QtGui import * 

from . import Aur
from . import Pacman

class Transaction:
    """An abstraction for interacting with the packaging system.
    """


    def __init__(self):
        """Initialize a new Transaction.
        """
        self.queryResult = []
        self.repoUpgrades = {}
        self.aurUpgrades = {}
        self.repoInstalls = {}
        self.aurInstalls = {}
        self.removes = {}
        self.aurDepends = {}
        self.aurBuildDepends = {}
        

    def sync(self):
        """Sync local databases with network mirror.
        """
        Pacman.sync()


    def getInstalled(self):
        """Returns a list of installed packages.
        """
        return Pacman.getInstalled()


    def toBeUpgraded(self):
        """Returns list of packages in need of upgrading.
        """
        pacUpgrade =  Pacman.toBeUpgraded()
        aurUpgrade = Aur.outOfDate()
        for app in aurUpgrade:
            pacUpgrade.append(app)
        return pacUpgrade


    def changeList(self, installList, upgradeList, removeList):
        """Parses changes.
        :param installLIst: List of files to install.
        :param upgradeList: List of files to upgrade.
        :param removeList: List of files to remove.
        """
        installed = self.getInstalled()
        for app in  list(installList.values()):
            if app['repo'] == 'aur':
                tInfo = Aur.getPkgInfo(app['Name'])
                self.aurInstalls[app['Name']] = app
            else:
                tInfo = Pacman.getPkgInfo(app['Name'])
                self.repoInstalls[app['Name']] = tInfo
        for app in  list(upgradeList.values()):
            if app['repo'] == 'aur':
                tInfo = Aur.getPkgInfo(app['Name'])
                self.aurUpgrades[app['Name']] = app
            else:
                tInfo = Pacman.getPkgInfo(app['Name'])
                self.repoUpgrades[app['Name']] = tInfo
        for app in  list(removeList.values()):
            tInfo = Pacman.getPkgInfo(app['Name'])
            self.removes[app['Name']] = tInfo

        rDict = {}
        rDict['repoInstalls'] = self.repoInstalls
        rDict['aurInstalls'] = self.aurInstalls
        rDict['repoUpgrades'] = self.repoUpgrades
        rDict['aurUpgrades'] = self.aurUpgrades
        rDict['removes'] = self.removes
        rDict['aurBuildDeps'] = self.aurBuildDepends
        rDict['aurDeps'] = self.aurDepends

        return rDict
        

    def upgrade(self, app):
        """Upgrade a given application.
        :param app: Application to upgrade.
        """
        installedList = Pacman.getInstalled()
        if app['repo'] == 'aur':
            upgrade = Aur.Upgrade(app['Name'])
            for bDep in upgrade.buildDepends:
                if bDep not in installedList:
                    recTransaction = Transaction()
                    recTransaction.upgrade(bDep)
            for dep in upgrade.depends:
                if dep not in installedList:
                    recTransaction = Transaction()
                    recTransaction.upgrade(dep)
            upgrade.makePkg()
            Pacman.installLocal(app['Name'])
        else:
            try:
                Pacman.install(app['Name'])
            except:
                pass
        


    def query(self, term):
        """Search for applications whose name and description contain <term>.
        :param term: Term to match against.
        """
        result = []
        installedList = Pacman.getInstalled()

        pDict = Pacman.search(term)
        for app in pDict:
            item = app
            if 'Name' not in item:
                continue
            if item['Name'] in installedList:
                item['Installed'] = True
            else:
                item['Installed'] = False
            result.append(app)

        aurQuery = Aur.Query(term)
        aurList = aurQuery.query

        if isinstance(aurList, list):
            for app in aurList:
                item = app
                item['repo'] = 'aur'
                if item['Name'] in installedList:
                    item['Installed'] = True
                else:
                    item['Installed'] = False
                result.append(app)

        self.queryResult = result
        


    def remove(self, app):
        """Remove given application.
        :param app: Application to remove.
        """
        Pacman.remove(app)




# vim: set ts=4 sw=4 noet:
