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

from . import Aur
from . import Pacman
from PyQt4.QtGui import * 

class Transaction:
    def __init__(self):
        self.queryResult = []
        self.repoUpgrades = {}
        self.aurUpgrades = {}
        self.repoInstalls = {}
        self.aurInstalls = {}
        self.removes = {}
        self.aurDepends = {}
        self.aurBuildDepends = {}
        

    def sync(self):
        Pacman.sync()

    def getInstalled(self):
        return Pacman.getInstalled()


    def toBeUpgraded(self):
        pacUpgrade =  Pacman.toBeUpgraded()
        aurUpgrade = Aur.outOfDate()
        for app in aurUpgrade:
            pacUpgrade.append(app)
        return pacUpgrade


    def changeList(self, installList, upgradeList, removeList):
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
        Pacman.remove(app)
