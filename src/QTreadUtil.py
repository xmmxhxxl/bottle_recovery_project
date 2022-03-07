# -*- coding = utf-8 -*-
# @Time : 2022/3/7 13:28
# @Author : liman
# @File : QTreadUtil.py
# @Software : PyCharm
import json
import random

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from paho.mqtt import client as mqtt_client

from DBUtil import DBUtilClass


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


# 用户窗口线程
class ReqUserInformationThread(QThread):
    reqUserSin = pyqtSignal(object, object)

    def __init__(self, openId, avatarUrl, parent=None):

        super(ReqUserInformationThread, self).__init__(parent)

        self.avatarUrl = avatarUrl
        self.openId = openId

        self.dbLink = DBUtilClass()
        self.reqUserInfo = False

    def run(self):
        while True:
            if self.reqUserInfo:
                avatar = QPixmap()
                avatar.loadFromData(requests.Session().get(self.avatarUrl).content)

                userInfo = self.dbLink.select_one("SELECT total FROM user_db WHERE `openId`=%s", [self.openId])

                self.reqUserSin.emit(avatar, userInfo)
                self.reqUserInfo = False


# 瓶子种类查询线程
class BottleFindThread(QThread):
    bottleFindSin = pyqtSignal(object, object, object, object)

    def __init__(self, parent=None):
        super(BottleFindThread, self).__init__(parent)

        self.dbLink = DBUtilClass()

        self.findSin = False
        self.bottleImageUrl = []
        self.reqImageUrlList = []
        self.bottleName = []
        self.bottleLabel = []
        self.bottlePrice = []

    def run(self):
        while True:
            if self.findSin:
                findBottleResult = self.dbLink.select_all("SELECT * FROM bottleInformation")
                for item in findBottleResult:
                    self.bottleImageUrl.append(item["imageUrl"])
                    self.bottleName.append(item["bottleName"])
                    self.bottleLabel.append(item["label"])
                    self.bottlePrice.append(item["bottlePrice"])

                for url in self.bottleImageUrl:
                    image = QPixmap()
                    image.loadFromData(requests.get(url=url).content)
                    self.reqImageUrlList.append(image)
                print(self.reqImageUrlList)
                self.bottleFindSin.emit(self.reqImageUrlList, self.bottleName, self.bottleLabel, self.bottlePrice)
                self.findSin = False
