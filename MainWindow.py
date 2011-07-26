#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2011 Thomas Schreiber
#
# Contributors:
#    Greg Haynes
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
from view.mwUi import Ui_MainWindow
from view.Dialogs import searchDialog
from view.Dialogs import syncDialog
from view.Dialogs import notRoot

from view.Changes import ChangeWin

import os, sys, time
import string
import shlex, subprocess
from model.Transaction import Transaction

class Main(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.makeConnections()

        self.installList = {}
        self.upgradeList = {}
        self.removeList = {}

        self.changeFont = QFont()
        self.changeFont.setBold(True)
        self.Font = QFont()
        self.Font.setBold(False)

        t = Transaction()
        self.installed = t.getInstalled()
        self.upgrades = {}


    def makeConnections(self):
        QObject.connect(self.ui.queryButton, SIGNAL('clicked()'), self.newSearch)
        QObject.connect(self.ui.queryEdit, SIGNAL('returnPressed()'), 
                        self.ui.queryButton, SIGNAL('clicked()'))
        QObject.connect(self.ui.actionSync, SIGNAL('triggered()'), self.newSync)
        QObject.connect(self.ui.actionView_Changes, SIGNAL('triggered()'), self.viewChanges)
        QObject.connect(self.ui.actionClear_Changes, SIGNAL('triggered()'), self.clearChanges)
        QObject.connect(self.ui.actionUpgrade, SIGNAL('triggered()'), self.markUpgrades)
        QObject.connect(self.ui.applyButton, SIGNAL('clicked()'), self.applyChanges)
        QObject.connect(self.ui.quitButton, SIGNAL('clicked()'), self.checkQuit)
        QObject.connect(self.ui.queryList, SIGNAL('itemSelectionChanged()'), self.handleChanges)


    def handleChanges(self):
        it = QTreeWidgetItemIterator(self.ui.queryList)
        while it.value():
            appName = str(it.value().text(2))
            if it.value().checkState(0):
                if appName not in self.installed and appName not in self.upgradeList:
                    # set bold
                    it.value().setFont(1, self.changeFont)
                    it.value().setFont(2, self.changeFont)
                    it.value().setFont(3, self.changeFont)
                    # add to installList
                    newInstall = {}
                    newInstall['Checked'] = it.value().checkState(0)
                    newInstall['repo'] = str(it.value().text(1))
                    newInstall['Name'] = str(it.value().text(2))
                    newInstall['Description'] = str(it.value().text(3))
                    if appName not in self.installList:
                        self.installList[appName] = newInstall
                elif appName in self.upgradeList:
                    it.value().setFont(1, self.changeFont)
                    it.value().setFont(2, self.changeFont)
                    it.value().setFont(3, self.changeFont)
                else:
                    it.value().setFont(1, self.Font)
                    it.value().setFont(2, self.Font)
                    it.value().setFont(3, self.Font)
                    if appName in self.removeList:
                        self.removeList.pop(appName)
            else:
                if appName in self.installed and appName not in self.upgradeList:
                    # set bold
                    it.value().setFont(1, self.changeFont)
                    it.value().setFont(2, self.changeFont)
                    it.value().setFont(3, self.changeFont)
                    # add to removeList 
                    newRemove = {}
                    newRemove['Checked'] = it.value().checkState(0)
                    newRemove['repo'] = str(it.value().text(1))
                    newRemove['Name'] = str(it.value().text(2))
                    newRemove['Description'] = str(it.value().text(3))
                    if appName not in self.removeList:
                        self.removeList[appName] = newRemove
                elif appName in self.upgradeList:
                    it.value().setFont(1, self.Font)
                    it.value().setFont(2, self.Font)
                    it.value().setFont(3, self.Font)
                    self.upgradeList.pop(appName)
                    if appName in self.installed:
                        it.value().setCheckState(0, Qt.Checked)
                else:
                    it.value().setFont(1, self.Font)
                    it.value().setFont(2, self.Font)
                    it.value().setFont(3, self.Font)
                    if appName in self.installList:
                        self.installList.pop(appName)
            it += 1


    def viewChanges(self):
        self.ui.queryList.clear()
        for app in list(self.installList.values()):
            item = QTreeWidgetItem([' ', app['repo'], 
                                    app['Name'], app['Description']])
            item.setCheckState(0,Qt.Checked)
            item.setFont(1, self.changeFont)
            item.setFont(2, self.changeFont)
            item.setFont(3, self.changeFont)
            self.ui.queryList.addTopLevelItem(item)
        for app in list(self.upgradeList.values()):
            item = QTreeWidgetItem([' ', app['repo'], 
                                    app['Name'], app['Description']])
            item.setCheckState(0,Qt.Checked)
            item.setFont(1, self.changeFont)
            item.setFont(2, self.changeFont)
            item.setFont(3, self.changeFont)
            self.ui.queryList.addTopLevelItem(item)
        for app in list(self.removeList.values()):
            item = QTreeWidgetItem([' ', app['repo'], 
                                    app['Name'], app['Description']])
            item.setCheckState(0,Qt.Unchecked)
            item.setFont(1, self.changeFont)
            item.setFont(2, self.changeFont)
            item.setFont(3, self.changeFont)
            self.ui.queryList.addTopLevelItem(item)
        self.ui.queryList.sortItems(2, Qt.AscendingOrder)


    def markUpgrades(self):
        t = Transaction()
        self.upgrades = t.toBeUpgraded()
        newT = Transaction()
        upgrades = newT.toBeUpgraded()
        for app in upgrades:
            if app['Name'] not in self.installList:
                self.upgradeList[app['Name']] = app
                


    def clearChanges(self):
        self.installList.clear()
        self.removeList.clear()
        self.upgradeList.clear()
        self.ui.queryList.clear()



    def newSearch(self):
        self.busy = searchDialog(self)
        self.ui.queryList.clear()

        self.busy.show()
        self.busy.setValue(0)

        self.q = runQuery(self)
        self.connect(self.q, SIGNAL("update(PyQt_PyObject)"), self.displaySearch)
        self.connect(self.busy, SIGNAL("canceled()"), self.cancelSearch)
        self.q.begin()


    def newSync(self):
        if os.geteuid() != 0:
            self.notroot = notRoot(self)
            QMessageBox.open(self.notroot)
            return

        self.sync = syncDialog(self)
        self.sync.show()
        self.sync.setValue(0)

        self.thread = runSync(self)
        self.connect(self.thread, SIGNAL("canceled()"), self.cancelSync)
        self.connect(self.thread, SIGNAL("finished()"), self.finishSync)
        self.thread.begin()


    def cancelSync(self):
        self.thread.terminate()
        self.sync.hide()

    def finishSync(self):
        self.sync.hide()


    # contributions by Greg Haynes
    def displaySearch(self, transaction):
        response = transaction.queryResult
        found_exact_match = False
        for q in response:
            item = QTreeWidgetItem([' ', q['repo'], 
                                    q['Name'], q['Description']])
            if q['Installed'] == True:
                item.setCheckState(0,Qt.Checked)
            else:
                item.setCheckState(0,Qt.Unchecked)
            self.ui.queryList.addTopLevelItem(item)
            if not found_exact_match and q['Name'].capitalize() == transaction.query_string.capitalize():
                item.setSelected(True)
        self.ui.queryList.sortItems(2, Qt.AscendingOrder)
        self.busy.hide()


    def cancelSearch(self):
        self.q.terminate()
        self.q = None


    def applyChanges(self):
        self.handleChanges()
        t = Transaction()
        changes = t.changeList(self.installList, self.upgradeList, self.removeList)
        cWin = ChangeWin(self)
        cWin.setChanges(changes)
        cWin.show()
         


    def checkQuit(self):
        app.quit()



class runQuery(QThread):
    '''Emits update(Transaction()) when complete.'''
    def __init__(self, mw):
        QThread.__init__(self)
        self.mw = mw


    def run(self):
        self.t = Transaction()
        self.t.query_string = str(mw.ui.queryEdit.text())
        self.t.query(self.t.query_string)
        self.emit(SIGNAL('update(PyQt_PyObject)'), self.t)
        return
        

    def begin(self):
        self.start()



class runSync(QThread):
    def __init__(self, mw):
        QThread.__init__(self)
        self.mw = mw


    def run(self):
        self.t = Transaction()
        self.t.sync()
        return


    def begin(self):
        self.start()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = Main()
    mw.show()
    sys.exit(app.exec_())
