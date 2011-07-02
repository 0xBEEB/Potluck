# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'proto.ui'
#
# Created: Fri Jul  1 20:23:40 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(439, 414)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 421, 381))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEdit = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setInputMask(_fromUtf8(""))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.lineEdit)
        self.queryButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.queryButton.setObjectName(_fromUtf8("queryButton"))
        self.horizontalLayout.addWidget(self.queryButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.treeWidget = QtGui.QTreeWidget(self.verticalLayoutWidget)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.header().setDefaultSectionSize(100)
        self.treeWidget.header().setSortIndicatorShown(False)
        self.verticalLayout.addWidget(self.treeWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setPlaceholderText(QtGui.QApplication.translate("MainWindow", "Cool App....", None, QtGui.QApplication.UnicodeUTF8))
        self.queryButton.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "Installed", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1, QtGui.QApplication.translate("MainWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(2, QtGui.QApplication.translate("MainWindow", "Description", None, QtGui.QApplication.UnicodeUTF8))

