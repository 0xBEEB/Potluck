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

# MainWindow.py
# by Thomas Schreiber <ubiquill@gmail.com>
#
# The main window for potluck, an AUR GUI frontend.

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from protoUi import Ui_MainWindow

import os, sys
from aur import *

class Main(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        QObject.connect(self.ui.queryButton, SIGNAL('clicked()'), self.newSearch)


    def newSearch(self):
        self.ui.queryList.clear()
        query = Query.QueryAUR(str(self.ui.queryEdit.text()))
        
        for q in query.query:
            item = QTreeWidgetItem([' ', q['Name'], q['Description']])
            self.ui.queryList.addTopLevelItem(item)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = Main()
    mw.show()
    sys.exit(app.exec_())
