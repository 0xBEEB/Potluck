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

import os, sys, time
import string
import shlex, subprocess
from aur import *

class Main(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        QObject.connect(self.ui.queryButton, SIGNAL('clicked()'), self.newSearch)
        QObject.connect(self.ui.queryEdit, SIGNAL('returnPressed()'), 
                        self.ui.queryButton, SIGNAL('clicked()'))


    def newSearch(self):
        self.busy = QProgressDialog(QString("Getting Package Information..."), QString("Cancel"), 0, 0, self)
        self.busy.setWindowModality(Qt.WindowModal)
        self.busy.setAutoReset(True)
        self.busy.setAutoClose(True)
        self.busy.setMinimum(0)
        self.busy.setMaximum(0)
        self.busy.resize(220,120)
        self.busy.setWindowTitle("Searching...")
        self.ui.queryList.clear()

        self.q = runQuery(self)

        self.busy.show()
        self.busy.setValue(0)
        app.processEvents()

        self.q.getQuery()

        while (self.q.finished == False):
            app.processEvents()
        self.busy.hide()


class runQuery(QThread):
    def __init__(self, mw):
        QThread.__init__(self, None)
        self.mw = mw
        self.finished = False


    def getQuery(self):
        app.processEvents()
        cmdOutput = subprocess.check_output(["pacman", "-Qeq"])
        app.processEvents()
        installed = string.split(cmdOutput, '\n')
        app.processEvents()
        query = Query.QueryAUR(str(self.mw.ui.queryEdit.text()))
        self.mw.busy.setLabelText(QString("Parsing Repsonse..."))
        
        for q in query.query:
            app.processEvents()
            item = QTreeWidgetItem([' ', q['Name'], q['Description']])
            if q['Name'] in installed:
                item.setCheckState(0,Qt.Checked)
            else:
                item.setCheckState(0,Qt.Unchecked)
            self.mw.ui.queryList.addTopLevelItem(item)
        self.finished = True




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = Main()
    mw.show()
    sys.exit(app.exec_())
