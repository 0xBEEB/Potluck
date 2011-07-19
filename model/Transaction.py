#!/usr/bin/env python2
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

import Aur
import Pacman
from PyQt4.QtGui import * 

class Transaction:
    def __init__(self):
        self.queryResult = []
        

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


    #def upgrade(self):


    def query(self, term):
        result = []
        installedList = Pacman.getInstalled()

        pDict = Pacman.search(term)
        for app in pDict:
            item = app
            if item[unicode('Name')] in installedList:
                item['Installed'] = True
            else:
                item['Installed'] = False
            result.append(app)

        aurQuery = Aur.Query(term)
        aurList = aurQuery.query

        if isinstance(aurList, list):
            for app in aurList:
                item = app
                item['repo'] = unicode('aur')
                if item['Name'] in installedList:
                    item['Installed'] = True
                else:
                    item['Installed'] = False
                result.append(app)

        self.queryResult = result
        


    def remove(self, app):
        Pacman.remove(app)
