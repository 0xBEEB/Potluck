# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'proto.ui'
#
# Created: Tue Jul  5 11:45:51 2011
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
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(439, 414)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setCursor(QtCore.Qt.ArrowCursor)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 421, 381))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.queryEdit = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.queryEdit.setInputMask(_fromUtf8(""))
        self.queryEdit.setObjectName(_fromUtf8("queryEdit"))
        self.horizontalLayout.addWidget(self.queryEdit)
        self.queryButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.queryButton.setObjectName(_fromUtf8("queryButton"))
        self.horizontalLayout.addWidget(self.queryButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.queryList = QtGui.QTreeWidget(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryList.sizePolicy().hasHeightForWidth())
        self.queryList.setSizePolicy(sizePolicy)
        self.queryList.setUniformRowHeights(True)
        self.queryList.setColumnCount(3)
        self.queryList.setObjectName(_fromUtf8("queryList"))
        self.queryList.header().setCascadingSectionResizes(True)
        self.queryList.header().setDefaultSectionSize(75)
        self.queryList.header().setHighlightSections(True)
        self.queryList.header().setMinimumSectionSize(5)
        self.queryList.header().setSortIndicatorShown(True)
        self.queryList.header().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.queryList)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Potluck", None, QtGui.QApplication.UnicodeUTF8))
        self.queryEdit.setPlaceholderText(QtGui.QApplication.translate("MainWindow", "Cool App....", None, QtGui.QApplication.UnicodeUTF8))
        self.queryButton.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.queryList.setSortingEnabled(True)
        self.queryList.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "Installed", None, QtGui.QApplication.UnicodeUTF8))
        self.queryList.headerItem().setText(1, QtGui.QApplication.translate("MainWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.queryList.headerItem().setText(2, QtGui.QApplication.translate("MainWindow", "Description", None, QtGui.QApplication.UnicodeUTF8))

