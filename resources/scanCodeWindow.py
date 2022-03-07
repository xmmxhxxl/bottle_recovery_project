# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanCodeWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_scanCodeWindow(object):
    def setupUi(self, scanCodeWindow):
        scanCodeWindow.setObjectName("scanCodeWindow")
        scanCodeWindow.resize(1024, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(scanCodeWindow.sizePolicy().hasHeightForWidth())
        scanCodeWindow.setSizePolicy(sizePolicy)
        scanCodeWindow.setMaximumSize(QtCore.QSize(1024, 600))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/mainWindow_ico/mainWindow_ico.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        scanCodeWindow.setWindowIcon(icon)
        scanCodeWindow.setStyleSheet("background-color:rgb(195, 227, 218)")
        self.gridLayout_2 = QtWidgets.QGridLayout(scanCodeWindow)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.scan_title_label = QtWidgets.QLabel(scanCodeWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scan_title_label.sizePolicy().hasHeightForWidth())
        self.scan_title_label.setSizePolicy(sizePolicy)
        self.scan_title_label.setMinimumSize(QtCore.QSize(250, 250))
        self.scan_title_label.setMaximumSize(QtCore.QSize(400, 400))
        self.scan_title_label.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"border-radius:3px;")
        self.scan_title_label.setText("")
        self.scan_title_label.setObjectName("scan_title_label")
        self.verticalLayout.addWidget(self.scan_title_label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 20, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.scan_qrcode_label = QtWidgets.QLabel(scanCodeWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scan_qrcode_label.sizePolicy().hasHeightForWidth())
        self.scan_qrcode_label.setSizePolicy(sizePolicy)
        self.scan_qrcode_label.setMaximumSize(QtCore.QSize(155, 41))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        self.scan_qrcode_label.setFont(font)
        self.scan_qrcode_label.setStyleSheet("border-radius: 1px;\n"
"background-color:rgb(195, 227, 218);\n"
"")
        self.scan_qrcode_label.setObjectName("scan_qrcode_label")
        self.horizontalLayout.addWidget(self.scan_qrcode_label)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 6)
        self.verticalLayout.setStretch(1, 1)
        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 1, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem5, 2, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(scanCodeWindow)
        QtCore.QMetaObject.connectSlotsByName(scanCodeWindow)

    def retranslateUi(self, scanCodeWindow):
        _translate = QtCore.QCoreApplication.translate
        scanCodeWindow.setWindowTitle(_translate("scanCodeWindow", "扫码"))
        self.scan_qrcode_label.setText(_translate("scanCodeWindow", "微信扫码登陆"))
import ico_src_rc
