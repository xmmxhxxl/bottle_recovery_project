# -*- coding = utf-8 -*-
# @Time : 2022/3/7 13:28
# @Author : liman
# @File : QTreadUtil.py
# @Software : PyCharm
import json
import random
import cv2 as cv
import requests
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QTableWidget

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


# 识别窗口线程
class BottleIdentifyThread(QThread):
    identifySin = pyqtSignal()

    def __init__(self, parent=None):
        super(BottleIdentifyThread, self).__init__(parent)

        # 摄像头初始化
        self.cap = cv.VideoCapture()
        self.playLabel = QLabel()
        self.resultTableWidget = QTableWidget()

        # 参数初始化
        self.length = 0
        self.frequency = 0
        self.image = None
        self.background = None
        self.frame = 10
        self.times = 0.5
        self.frameNumber = 0
        self.mseList = np.array([0] * 3)
        self.es = None

        self.playVideo = True
        self.capOpen = True

    # 线程主体
    def run(self):

        self.cap = cv.VideoCapture(0)
        while self.playVideo:
            self.frameNumber += 1
            grabbed, self.image = self.cap.read()

            if self.frameNumber == self.frame:
                midimg = self.image
            elif self.frameNumber % self.frame == 0:
                self.oldimg = midimg
                self.nowimg = self.image
                midimg = self.image

                # 对帧进行预处理，先转灰度图，再进行高斯模糊
                gray_frame = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
                gray_frame = cv.GaussianBlur(gray_frame, (21, 21), 0)

                if self.background is None:
                    self.background = gray_frame
                    continue

                diff = cv.absdiff(self.background, gray_frame)
                diff = cv.threshold(diff, 25, 25, cv.THRESH_BINARY)[1]
                diff = cv.dilate(diff, cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 4)), iterations=2)

                contours, hierarchy = cv.findContours(diff.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                # 计算画面变化的面积、显示轮廓
                for c in contours:
                    if cv.contourArea(c) < 4000:
                        continue
                    (x, y, w, h) = cv.boundingRect(c)
                    cv.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # 显示画面
                showImage = QImage(self.image, self.image.shape[1], self.image.shape[0], QImage.Format_BGR888)
                self.playLabel.setPixmap(QPixmap.fromImage(showImage))

                if self.frameNumber % (self.frame * self.times) == 0:
                    # 计算前后两帧的MSE(均方误差)
                    MSE = np.sum((self.oldimg.astype('float') - self.nowimg.astype('float')) ** 2)
                    # 数据归一化
                    MSE /= float(self.oldimg.shape[0] * self.oldimg.shape[1])

                    # 将MSE添加到列表中
                    self.mseList[self.length] = round(MSE, 3)
                    self.length += 1
                    if self.length >= 3:
                        self.length = 0

                    print(self.mseList)
                    variance = round(np.var(self.mseList), 5)
                    average = round(np.mean(self.mseList), 5)

                    print(variance, average)

                    if variance > 10000 and average > 500:
                        self.frequency += 1
                        cv.imwrite("../img/image{}.png".format(self.length), self.image)
                        print("success write image")
                    elif variance < 5000 and variance < 500 and self.frequency >= 2:
                        print("touch off")
                        self.identifySin.emit()
                        self.frequency = 0
