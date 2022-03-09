# -*- coding = utf-8 -*-
# @Time : 2022/3/6 13:52
# @Author : liman
# @File : firstWindow.py
# @Software : PyCharm
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QLabel, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5 import QtCore

from scanCodeWindow import Ui_scanCodeWindow
from convertWindow import Ui_convertWindow
from mainWindow import Ui_mainWindow
from userWindow import Ui_userWindow
from kindWindow import Ui_kindWindow

from QTreadUtil import MQTTThread, ReqUserInformationThread, BottleFindThread, BottleIdentifyThread, \
    GetBottleIdentifyResultThread, InsertDataThread, ServoThread

"""
   主窗口
"""


class FirstWindow(QDialog, Ui_mainWindow):

    def __init__(self, openId, nickName, avatarUrl, ):
        super(FirstWindow, self).__init__()

        # 初始化
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        # 设置用户数据
        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

        # 设置按键响应
        self.main_account_but.clicked.connect(self.account_but_clicked)
        self.main_identify_but.clicked.connect(self.identify_but_clicked)
        self.main_examine_but.clicked.connect(self.user_but_clicked)
        self.main_log_out_but.clicked.connect(self.user_log_out_clicked)

        # 窗口初始化
        self.showConvertWindow = None
        self.showKindWindow = None
        self.showUserWindow = None
        self.showScanCodeWindow = None

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
        self.showScanCodeWindow = ScanCodeWindow(True)
        self.showScanCodeWindow.show()


"""
    扫码窗口,用户扫码进行登录
"""


class ScanCodeWindow(QWidget, Ui_scanCodeWindow):

    def __init__(self, mqttStart, parent=None):
        super(ScanCodeWindow, self).__init__(parent)

        # 初始化
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.showMainWindow = None

        # mqtt线程
        self.mqtt = MQTTThread(subscribeTopic=mqttStart)
        self.mqtt.user_sin.connect(self.setUserInformation)
        self.mqtt.start()

    # 显示用户
    def setUserInformation(self, openId, nickName, avatarUrl):
        self.hide()
        self.mqtt.receiverData = False
        self.showMainWindow = FirstWindow(openId, nickName, avatarUrl)
        self.showMainWindow.show()


"""
    识别窗口,显示视频流,显示瓶子识别信息
"""


class ConvertWindow(QWidget, Ui_convertWindow):

    def __init__(self, openId, nickName, avatarUrl):
        super(ConvertWindow, self).__init__()
        self.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        # 设置表不可编辑、表头自动伸缩
        self.resultTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.showMainWindow = None

        # 设置用户信息
        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

        # 识别线程
        self.playVideo = BottleIdentifyThread()
        self.playVideo.playLabel = self.videoLabel
        self.playVideo.resultTableWidget = self.resultTableWidget
        self.playVideo.cue = self.cue_label
        self.playVideo.identifySin.connect(self.setIdentifySpecies)
        self.playVideo.start()

        # 获取识别数据线程
        self.identifyResult = GetBottleIdentifyResultThread()
        self.identifyResult.identifyStart = False
        self.identifyResult.getIdentifyResult.connect(self.setBottleInformation)
        self.bottleNameList = []
        self.bottlePriceList = []

        # 数据库插入线程
        self.insertData = InsertDataThread()
        self.insertData.start()

        # 舵机启动线程
        self.servo = ServoThread()
        self.servo.start()

        # 按键响应
        self.back_main_but.clicked.connect(self.backMainWindow)

    def backMainWindow(self):
        self.hide()
        self.playVideo.playVideo = False
        self.servo.servo.stopServo()
        self.showMainWindow = FirstWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showMainWindow.show()

    # 视频现成响应槽
    def setIdentifySpecies(self):
        self.identifyResult.start()
        self.identifyResult.identifyStart = True

    # 识别结果响应槽
    def setBottleInformation(self, bottleName, bottleLabel, bottlePrice, bottleSimilarity):
        print(bottleName, bottleLabel, bottlePrice, bottleSimilarity, self.setOpenId)
        row = self.resultTableWidget.rowCount()
        if bottleSimilarity > 50:
            self.resultTableWidget.insertRow(row)

            bottleNameItem = QTableWidgetItem(str(bottleName))
            bottlePriceItem = QTableWidgetItem(str(bottlePrice))
            bottleNameItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            bottlePriceItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            self.resultTableWidget.setItem(row, 0, bottlePriceItem)
            self.resultTableWidget.setItem(row, 1, bottleNameItem)

            QApplication.processEvents()

            self.insertData.label = bottleLabel
            self.insertData.name = bottleName
            self.insertData.price = bottlePrice
            self.insertData.openId = self.setOpenId

            self.servo.startServo = True
            self.insertData.insertDataSin = True


'''
            rows = self.resultTableWidget.rowCount()
            for item in range(0, rows):
                price = self.resultTableWidget.item(item, 0).text()
                totalPrice += eval(price)

            self.resultTableWidget.insertRow(rows)

            bottleTileItem = QTableWidgetItem(str("总价"))
            bottleTotalPriceItem = QTableWidgetItem(str(totalPrice))

            bottleTileItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            bottleTotalPriceItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            self.resultTableWidget.setItem(rows, 1, bottleTileItem)
            self.resultTableWidget.setItem(rows, 0, bottleTotalPriceItem)
'''

"""
    用户窗口,显示用户信息
"""


class UserWindow(QWidget, Ui_userWindow):

    def __init__(self, openId, nickName, avatarUrl, parent=None):
        super(UserWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.showMainWindow = None

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


"""
    瓶子种类显示窗口,显示可回收的瓶子种类信息
"""


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
        self.showMainWindow = None

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

            bottleNameItem = QTableWidgetItem(str(bottleName[item]))
            bottleLabelItem = QTableWidgetItem(str(bottlePrice[item]))

            # 设置单元格居中
            bottleNameItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            bottleLabelItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            self.kind_infortion_table.setItem(item, 1, bottleNameItem)
            self.kind_infortion_table.setItem(item, 2, bottleLabelItem)

            QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    show = ScanCodeWindow(True)
    show.show()
    sys.exit(app.exec_())
