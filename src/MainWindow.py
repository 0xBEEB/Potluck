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

# PyQt4 objects and functions
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# UI components
from view.mwUi import Ui_MainWindow
from view.Dialogs import searchDialog
from view.Dialogs import syncDialog
from view.Dialogs import commitDialog
from view.Dialogs import notRoot

from view.Changes import ChangeWin

# Package management
from model.Transaction import Transaction

# General Python Libraries
import os, sys, time
import string
import shlex, subprocess

class Main(QMainWindow):
    """The main window of the application.
    :param QMainWindow: A Qt parent class for Main Windows.
    """


    def __init__(self, app):
        """Initialize the window.
        :param app: Parent Qt application.
        """
        QMainWindow.__init__(self)
        self.app = app

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
        """Connects signals and slots for the main window.
        """
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
        """Updates the list of packages when a checkbox is (un)checked.
        """
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
        """Displays the list of packages that have been selected to change
        state.
        """
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
        """Finds all packages that can be updated, and marks them for \
        updating.
        """
        t = Transaction()
        self.upgrades = t.toBeUpgraded()
        newT = Transaction()
        upgrades = newT.toBeUpgraded()
        for app in upgrades:
            if app['Name'] not in self.installList:
                self.upgradeList[app['Name']] = app
                


    def clearChanges(self):
        """Clears all changes that have not been commited.
        """
        self.ui.queryList.clear()
        self.installList.clear()
        self.removeList.clear()
        self.upgradeList.clear()
        self.handleChanges()



    def newSearch(self):
        """Brings up a dialog while searching occurs.
        """
        self.busy = searchDialog(self)
        self.ui.queryList.clear()

        self.busy.show()
        self.busy.setValue(0)

        self.q = runQuery(self)
        self.connect(self.q, SIGNAL("update(PyQt_PyObject)"), self.displaySearch)
        self.connect(self.busy, SIGNAL("canceled()"), self.cancelSearch)
        self.q.begin()


    def newSync(self):
        """Brings up a dialog while syncing package database.
        """
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
        """Cancels sync operation.
        """
        self.thread.terminate()
        self.sync.hide()

    def finishSync(self):
        """Hides sync dialog upon completion of sync operation.
        """
        self.sync.hide()


    # contributions by Greg Haynes
    def displaySearch(self, transaction):
        """Displays the results of a search operation.
        :param transaction: A transaction initiated for searching.
        """
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
        """Cancels search and returns user to Main window.
        """
        self.q.terminate()
        self.q = None


    def applyChanges(self):
        """Displays changes and commits them.
        """
        if os.geteuid() != 0:
            self.notroot = notRoot(self)
            QMessageBox.open(self.notroot)
            return
        self.handleChanges()
        t = Transaction()
        changes = t.changeList(self.installList, self.upgradeList, self.removeList)
        self.cWin = ChangeWin(self)
        QObject.connect(self.cWin, SIGNAL('accepted()'), self.commitChanges)
        QObject.connect(self.cWin, SIGNAL('rejected()'), self.noChanges)
        self.cWin.setChanges(changes)
        self.cWin.show()

    def noChanges(self):
        """Closes the change dialog.
        """
        self.cWin.hide()
         

    def commitChanges(self):
        """If changes were accepted they are commited.
        """
        tLen = len(self.installList) + len(self.upgradeList) + len(self.removeList)
        self.commitWin = commitDialog(self)
        self.commitWin.show()
        self.commitWin.setValue(0)
        if len(self.removeList) > 0:
            self.commitWin.setLabel(QLabel(str('Removing Packages')))
            self.commitRemoves()
        if len(self.upgradeList) > 0:
            self.commitWin.setLabel(QLabel(str('Upgrading Packages')))
            self.commitUpgrades()
        if len(self.installList) > 0:
            self.commitWin.setLabel(QLabel(str('Installing Packages')))
            self.commitInstalls()


    def commitRemoves(self):
        """Removes programs marked as such.
        """
        for app in self.removeList:
            try:
                self.commitWin.setLabel(QLabel(str('Removing ' + app['Name'])))
                trans = Transaction()
                trans.remove(app['Name'])
            except:
                pass


    def commitUpgrades(self):
        """Upgrades programs marked as such.
        """
        for app in self.upgradeList:
            try:
                self.commitWin.setLabel(QLabel(str('Upgrading ' + app['Name'])))
                trans = Transaction()
                trans.upgrade(app)
            except:
                pass


    def commitInstalls(self):
        """Installs programs marked as such.
        """
        for app in self.installList:
            try:
                self.commitWin.setLabel(QLabel(str('Installing ' + app['Name'])))
                trans = Transaction()
                trans.upgrade(app)
                Pacman.install(app['Name'])
            except:
                pass
        
        
    def checkQuit(self):
        """Exit the application.
        """
        self.app.quit()




class runQuery(QThread):
    """Emits update(Transaction()) when complete.
    :Param QThread: Parent class.
    """


    def __init__(self, mw):
        QThread.__init__(self)
        self.mw = mw


    def run(self):
        """Runs query in a seperate thread.
        """
        self.t = Transaction()
        self.t.query_string = str(self.mw.ui.queryEdit.text())
        self.t.query(self.t.query_string)
        self.emit(SIGNAL('update(PyQt_PyObject)'), self.t)
        return
        

    def begin(self):
        """Begin new query thread.
        """
        self.start()




class runSync(QThread):
    """Thread for syncing the package database.
    :param QThread: Parent class.
    """


    def __init__(self, mw):
        """Initialize new sync thread.
        :param mw: MainWindow that created this class.
        """
        QThread.__init__(self)
        self.mw = mw


    def run(self):
        """Run sync thread.
        """
        self.t = Transaction()
        self.t.sync()
        return


    def begin(self):
        """Begin new Thread.
        """
        self.start()




# Run if called directly
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = Main(app)
    mw.show()
    sys.exit(app.exec_())


# vim: set ts=4 sw=4 noet:
