# -*- coding = utf-8 -*-
# @Time : 2022/3/6 13:52
# @Author : liman
# @File : firstWindow.py
# @Software : PyCharm
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QLabel, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5 import QtCore

from resources.scanCodeWindow import Ui_scanCodeWindow
from resources.convertWindow import Ui_convertWindow
from resources.mainWindow import Ui_mainWindow
from resources.userWindow import Ui_userWindow
from resources.kindWindow import Ui_kindWindow

from QTreadUtil import MQTTThread, ReqUserInformationThread, BottleFindThread


# 主窗口
class FirstWindow(QDialog, Ui_mainWindow):

    def __init__(self, openId, nickName, avatarUrl, ):
        super(FirstWindow, self).__init__()

        # 初始化
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        # 实例化窗口类
        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

        # 设置按键响应
        self.main_account_but.clicked.connect(self.account_but_clicked)
        self.main_identify_but.clicked.connect(self.identify_but_clicked)
        self.main_examine_but.clicked.connect(self.user_but_clicked)
        self.main_log_out_but.clicked.connect(self.user_log_out_clicked)


    # 设置槽函数
    def account_but_clicked(self):
        self.hide()
        self.showConvertWindow = ConvertWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showConvertWindow.show()

    def identify_but_clicked(self):
        self.hide()
        self.showKindWindow = KindWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showKindWindow.show()

    def user_but_clicked(self):
        self.hide()
        self.showUserWindow = UserWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showUserWindow.show()

    def user_log_out_clicked(self):
        self.hide()
        self.showscanCodeWindow = ScanCodeWindow()
        self.showscanCodeWindow.show()


# 扫码窗口
class ScanCodeWindow(QWidget, Ui_scanCodeWindow):

    def __init__(self, parent=None):
        super(ScanCodeWindow, self).__init__(parent)

        # 初始化
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        # mqtt线程
        self.mqtt = MQTTThread()
        self.mqtt.user_sin.connect(self.setUserInformation)
        self.mqtt.start()

    # 显示用户
    def setUserInformation(self, openId, nickName, avatarUrl):
        self.hide()
        self.showMainWindow = FirstWindow(openId, nickName, avatarUrl)
        self.showMainWindow.show()


# 识别窗口
class ConvertWindow(QWidget, Ui_convertWindow):

    def __init__(self, openId, nickName, avatarUrl):
        super(ConvertWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl
        self.back_main_but.clicked.connect(self.backMainWindow)

    def backMainWindow(self):
        self.hide()
        self.showMainWindow = FirstWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showMainWindow.show()


# 用户窗口
class UserWindow(QWidget, Ui_userWindow):

    def __init__(self, openId, nickName, avatarUrl, parent=None):
        super(UserWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

        self.user_back_but.clicked.connect(self.backMainWindow)

        self.reqUserInfoThread = ReqUserInformationThread(self.setOpenId, self.setAvatarUrl)
        self.reqUserInfoThread.reqUserSin.connect(self.setUserInformation)
        self.reqUserInfoThread.reqUserInfo = True

        self.reqUserInfoThread.start()

    # 窗口跳转
    def backMainWindow(self):
        self.hide()
        self.showMainWindow = FirstWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showMainWindow.show()

    # 设置用户信息
    def setUserInformation(self, avatarUrlSet, userTotal):
        self.user_headportrait_icon.setPixmap(avatarUrlSet)
        self.user_name_label.setText(self.setNickName)
        self.user_account_number.setText(str(userTotal["total"]))
        self.user_coupon_number.setText("0")
        self.user_integration_number.setText("0")
        self.user_reward_number.setText("0")


# 种类窗口
class KindWindow(QWidget, Ui_kindWindow):

    def __init__(self, openId, nickName, avatarUrl):
        super(KindWindow, self).__init__()

        # 窗口初始化信息
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.kind_infortion_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.kind_infortion_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.kind_infortion_table.verticalHeader().setVisible(False)
        self.kind_infortion_table.horizontalHeader().setVisible(False)
        self.kind_infortion_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置用户参数
        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

        # 实例化查找种类的线程、设置信号槽
        self.findBottleInformation = BottleFindThread()
        self.findBottleInformation.findSin = True
        self.findBottleInformation.bottleFindSin.connect(self.setBottleData)
        self.findBottleInformation.start()

        self.kind_back_but.clicked.connect(self.backMainWindow)

    # 返回主窗口
    def backMainWindow(self):
        self.hide()
        self.showMainWindow = FirstWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showMainWindow.show()

    # 设置种类信息
    def setBottleData(self, bottleImageUrl, bottleName, bottleLabel, bottlePrice):
        self.label.setText("为您查询到以下信息")
        for item in range(0, len(bottleName)):
            image = QLabel(self)
            image.setPixmap(bottleImageUrl[item])

            # 图片自适应
            image.setScaledContents(True)
            image.setMaximumSize(132, 132)

            # 指定单元格的大小
            self.kind_infortion_table.insertRow(item)
            self.kind_infortion_table.setRowHeight(item, 132)
            self.kind_infortion_table.setColumnWidth(item, 132)

            # 显示信息
            self.kind_infortion_table.setCellWidget(item, 0, image)
            self.kind_infortion_table.setItem(item, 1, QTableWidgetItem(bottleName[item]))
            self.kind_infortion_table.setItem(item, 2, QTableWidgetItem(str(bottlePrice[item])))
            QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    show = ScanCodeWindow()
    show.show()
    sys.exit(app.exec_())
