# -*- coding = utf-8 -*-
# @Time : 2022/3/6 13:52
# @Author : liman
# @File : firstWindow.py
# @Software : PyCharm
import json
import random
import sys

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDialog
from PyQt5 import QtCore

from paho.mqtt import client as mqtt_client

from resources.scanCodeWindow import Ui_scanCodeWindow
from resources.convertWindow import Ui_convertWindow
from resources.mainWindow import Ui_mainWindow
from resources.userWindow import Ui_userWindow
from resources.kindWindow import Ui_kindWindow


# 主窗口
class FirstWindow(QDialog, Ui_mainWindow):

    def __init__(self, openId, nickName, avatarUrl, ):
        super(FirstWindow, self).__init__()

        # 初始化
        self.mainWindowSetupUi(self)
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


# 扫码窗口
class ScanCodeWindow(QWidget, Ui_scanCodeWindow):

    def __init__(self, parent=None):
        super(ScanCodeWindow, self).__init__(parent)

        # 初始化
        self.scanCodeWindowSetupUi(self)
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
        self.convertWindowSetupUi(self)
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
        self.userWindowSetupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

        self.user_back_but.clicked.connect(self.backMainWindow)
        self.setUserInformation()

    # 窗口跳转
    def backMainWindow(self):
        self.hide()
        self.showMainWindow = FirstWindow(self.setOpenId, self.setNickName, self.setAvatarUrl)
        self.showMainWindow.show()

    # 设置用户信息
    def setUserInformation(self):
        avatar = QPixmap()
        avatar.loadFromData(requests.Session().get(url=self.setAvatarUrl).content)
        self.user_headportrait_icon.setPixmap(avatar)
        self.user_name_label.setText(self.setNickName)


# 种类窗口
class KindWindow(QWidget, Ui_kindWindow):

    def __init__(self, openId, nickName, avatarUrl):
        super(KindWindow, self).__init__()
        self.kindWindowSetupUi(self)
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


# mqtt线程
class MQTTThread(QThread):
    user_sin = pyqtSignal(object, object, object)
    switch_sin = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MQTTThread, self).__init__(parent)

        self.broker = 'www.xmxhxl.top'
        self.port = 1883
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def subscribe(self, client: mqtt_client, topic):
        def on_message(client, userdata, msg):
            data = json.loads(msg.payload.decode())
            if msg.topic == 'user/openId':
                self.user_sin.emit(data['openId'], data['nickName'], data['avatarUrl'])
                print(data)
            else:
                self.switch_sin.emit(data['msg'])

        client.subscribe(topic)
        client.on_message = on_message

    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client, "user/#")
        client.loop_forever()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    show = ScanCodeWindow()
    show.show()
    sys.exit(app.exec_())
