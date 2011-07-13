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

# potluck
# by Thomas Schreiber <ubiquill@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class searchDialog(QProgressDialog):
    def __init__(self, parent):
        QProgressDialog.__init__(self, parent)
        #QProgressDialog(QString("Searching..."), QString("Cancel"), 0, 0, self)
        self.setLabel(QLabel(QString("Searching...")))
        self.setWindowModality(Qt.WindowModal)
        self.setAutoReset(True)
        self.setAutoClose(True)
        self.setMinimum(0)
        self.setMaximum(0)
        self.resize(220,120)
        self.setWindowTitle("Searching...")
