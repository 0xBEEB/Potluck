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

# by Thomas Schreiber <ubiquill@gmail.com>
#

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from view.changesUi import Ui_changeSummary

import string

class ChangeWin(QDialog):
    """A QDialog that lists changes before they are commited.
    :param QDialog: Parent class.
    """


    def __init__(self, parent):
        """Initialize ChangeWin.
        :param parent: Caller.
        """
        QDialog.__init__(self, parent)
        self.ui=Ui_changeSummary()
        self.ui.setupUi(self)


    def setChanges(self, changeDict):
        """Add changes to ChangeWin.
        :param changeDict: Dictionary of changes.
        """
        installString = ''
        upgradeString = ''
        removeString = ''
        for app in changeDict['repoInstalls']:
            installString += app + ' '
        for app in changeDict['aurInstalls']:
            installString += app + ' '
        for app in changeDict['aurBuildDeps']:
            installString += app + ' '
        for app in changeDict['aurDeps']:
            installString += app + ' '
        for app in changeDict['repoUpgrades']:
            upgradeString += app + ' '
        for app in changeDict['aurUpgrades']:
            upgradeString += app + ' '
        for app in changeDict['removes']:
            removeString += app + ' '

        self.ui.toInstallEdit.setText(installString)
        self.ui.toUpgradeEdit.setText(upgradeString)
        self.ui.toRemoveEdit.setText(removeString)




# vim: set ts=4 sw=4 noet:
