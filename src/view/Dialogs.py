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

# potluck
# by Thomas Schreiber <ubiquill@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class searchDialog(QProgressDialog):
    """Dialog shown while searching.
    """
    def __init__(self, parent):
        QProgressDialog.__init__(self, parent)
        #QProgressDialog(QString("Searching..."), QString("Cancel"), 0, 0, self)
        searchString = str('Searching...')
        searchLabel = QLabel(searchString)
        self.setLabel(searchLabel)
        self.setWindowModality(Qt.WindowModal)
        self.setAutoReset(True)
        self.setAutoClose(True)
        self.setMinimum(0)
        self.setMaximum(0)
        self.resize(220,120)
        self.setWindowTitle("Searching...")




class syncDialog(QProgressDialog):
    """Dialog shown while syncing.
    """
    def __init__(self, parent):
        QProgressDialog.__init__(self, parent)
        self.setLabel(QLabel(str("Syncing...")))
        self.setWindowModality(Qt.WindowModal)
        self.setAutoReset(True)
        self.setAutoClose(True)
        self.setMinimum(0)
        self.setMaximum(0)
        self.resize(220,120)
        self.setWindowTitle("Syncing...")




class commitDialog(QProgressDialog):
    """Dialog shown while commiting changes.
    """
    def __init__(self, parent):
        QProgressDialog.__init__(self, parent)
        statusString = str('Preparing Changes')
        statusLabel = QLabel(statusString)
        self.setLabel(statusLabel)
        self.setWindowModality(Qt.WindowModal)
        self.setAutoReset(True)
        self.setAutoClose(True)
        self.setMinimum(0)
        self.setMaximum(0)
        self.resize(220,120)
        self.setWindowTitle("Commiting Changes")




class notRoot(QMessageBox):
    """MessageBox shown when operations require escalated priviledges.
    """
    def __init__(self, parent):
        QMessageBox.__init__(self, parent)
        self.setDefaultButton(QMessageBox.Ok)
        self.setWindowModality(Qt.WindowModal)
        self.setText(str('You must be root to complete this action'))
        self.setWindowTitle("Error")




# vim: set ts=4 sw=4 noet:
