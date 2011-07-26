# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'changes.ui'
#
# Created: Tue Jul 26 11:14:57 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_changeSummary(object):
    def setupUi(self, changeSummary):
        changeSummary.setObjectName(_fromUtf8("changeSummary"))
        changeSummary.resize(400, 300)
        changeSummary.setModal(True)
        self.verticalLayoutWidget = QtGui.QWidget(changeSummary)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 381, 281))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.declarationHeader = QtGui.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.declarationHeader.setFont(font)
        self.declarationHeader.setObjectName(_fromUtf8("declarationHeader"))
        self.verticalLayout.addWidget(self.declarationHeader)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.installDeclaration = QtGui.QLabel(self.verticalLayoutWidget)
        self.installDeclaration.setObjectName(_fromUtf8("installDeclaration"))
        self.horizontalLayout.addWidget(self.installDeclaration)
        self.toInstallEdit = QtGui.QLabel(self.verticalLayoutWidget)
        self.toInstallEdit.setText(_fromUtf8(""))
        self.toInstallEdit.setObjectName(_fromUtf8("toInstallEdit"))
        self.horizontalLayout.addWidget(self.toInstallEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.toUpgradeDeclaration = QtGui.QLabel(self.verticalLayoutWidget)
        self.toUpgradeDeclaration.setObjectName(_fromUtf8("toUpgradeDeclaration"))
        self.horizontalLayout_3.addWidget(self.toUpgradeDeclaration)
        self.toUpgradeEdit = QtGui.QLabel(self.verticalLayoutWidget)
        self.toUpgradeEdit.setText(_fromUtf8(""))
        self.toUpgradeEdit.setObjectName(_fromUtf8("toUpgradeEdit"))
        self.horizontalLayout_3.addWidget(self.toUpgradeEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.toRemoveDeclaration = QtGui.QLabel(self.verticalLayoutWidget)
        self.toRemoveDeclaration.setObjectName(_fromUtf8("toRemoveDeclaration"))
        self.horizontalLayout_2.addWidget(self.toRemoveDeclaration)
        self.toRemoveEdit = QtGui.QLabel(self.verticalLayoutWidget)
        self.toRemoveEdit.setText(_fromUtf8(""))
        self.toRemoveEdit.setObjectName(_fromUtf8("toRemoveEdit"))
        self.horizontalLayout_2.addWidget(self.toRemoveEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(changeSummary)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), changeSummary.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), changeSummary.reject)
        QtCore.QMetaObject.connectSlotsByName(changeSummary)

    def retranslateUi(self, changeSummary):
        changeSummary.setWindowTitle(QtGui.QApplication.translate("changeSummary", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.declarationHeader.setText(QtGui.QApplication.translate("changeSummary", "Changes:", None, QtGui.QApplication.UnicodeUTF8))
        self.installDeclaration.setText(QtGui.QApplication.translate("changeSummary", "To be installed:", None, QtGui.QApplication.UnicodeUTF8))
        self.toUpgradeDeclaration.setText(QtGui.QApplication.translate("changeSummary", "To be Upgraded", None, QtGui.QApplication.UnicodeUTF8))
        self.toRemoveDeclaration.setText(QtGui.QApplication.translate("changeSummary", "To be removed:", None, QtGui.QApplication.UnicodeUTF8))

