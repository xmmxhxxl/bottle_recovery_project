# -*- coding = utf-8 -*-
# @Time : 2022/3/7 13:28
# @Author : liman
# @File : QTreadUtil.py
# @Software : PyCharm
import json
import random
import socket
import time

import cv2 as cv
import requests
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QTableWidget

from paho.mqtt import client as mqtt_client

from DBUtil import DBUtilClass
from IdentifyUtil import IdentifyUtil
from ServoUtil import Servo

"""
    MQTT线程,MQTT服务器的订阅、收发数据
"""


class MQTTThread(QThread):
    user_sin = pyqtSignal(object, object, object)
    switch_sin = pyqtSignal(str)

    def __init__(self, subscribeTopic, parent=None):
        super(MQTTThread, self).__init__(parent)

        self.broker = 'www.xmxhxl.top'
        self.port = 1883
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.receiverData = True
        self.subscribeTopic = subscribeTopic

    def connect_mqtt(self) -> mqtt_client:
        try:
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    print("Connected to MQTT Broker!")
                else:
                    print("Failed to connect, return code %d\n", rc)

            client = mqtt_client.Client(self.client_id)
            client.on_connect = on_connect
            client.connect(self.broker, self.port)
            return client
        except Exception as ex:
            print("MQTTThread -> connect_mqtt :", ex)

    def subscribe(self, client: mqtt_client, topic):
        try:
            def on_message(client, userdata, msg):
                data = json.loads(msg.payload.decode())
                if self.receiverData:
                    if msg.topic == 'user/userInfo':
                        self.user_sin.emit(data['openId'], data['nickName'], data['avatarUrl'])
                        print(data)

            client.subscribe(topic)
            client.on_message = on_message
        except Exception as ex:
            print("MQTTThread -> subscribe :", ex)

    # socket.gaierror
    def run(self):
        try:
            if self.subscribeTopic:
                client = self.connect_mqtt()
                self.subscribe(client, "user/userInfo")
                client.loop_forever()
            else:
                time.sleep(0.5)
        except socket.gaierror and Exception as ex:
            print("MQTTThread -> run :", ex)


"""
    用户窗口,请求用户头像,余额等信息,防止界面卡顿
"""


class ReqUserInformationThread(QThread):
    reqUserSin = pyqtSignal(object, object)

    def __init__(self, openId, avatarUrl, parent=None):

        super(ReqUserInformationThread, self).__init__(parent)

        self.avatarUrl = avatarUrl
        self.openId = openId
        try:
            self.dbLink = DBUtilClass()
            self.reqUserInfo = False
            self.session = requests.Session()
        except Exception as ex:
            print("ReqUserInformationThread -> init :", ex)

    def run(self):
        while True:
            try:
                if self.reqUserInfo:
                    start = time.time()
                    avatar = QPixmap()
                    avatar.loadFromData(self.session.get(self.avatarUrl).content)

                    userInfo = self.dbLink.select_one("SELECT total FROM user_db WHERE `openId`=%s", [self.openId])

                    self.reqUserSin.emit(avatar, userInfo)
                    self.reqUserInfo = False
                    print("请求时间", time.time() - start)
                else:
                    time.sleep(0.5)
            except Exception as ex:
                print("ReqUserInformationThread -> run :", ex)


"""
    请求oss服务器的瓶子种类照片、查询数据库中的瓶子种类和数据
"""


class BottleFindThread(QThread):
    bottleFindSin = pyqtSignal(object, object, object, object)

    def __init__(self, parent=None):
        super(BottleFindThread, self).__init__(parent)

        try:
            self.dbLink = DBUtilClass()
        except Exception as ex:
            try:
                self.dbLink = DBUtilClass()
            except Exception as ex:
                print("BottleFindThread -> DBUtilClass :", ex)
        self.findSin = False
        self.bottleImageUrl = []
        self.reqImageUrlList = []
        self.bottleName = []
        self.bottleLabel = []
        self.bottlePrice = []
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"}

    def run(self):
        while True:
            try:
                if self.findSin:
                    start = time.time()
                    findBottleResult = self.dbLink.select_all("SELECT * FROM bottleInformation")
                    for item in findBottleResult:
                        self.bottleImageUrl.append(item["imageUrl"])
                        self.bottleName.append(item["bottleName"])
                        self.bottleLabel.append(item["bottleLabel"])
                        self.bottlePrice.append(item["bottlePrice"])

                    for url in self.bottleImageUrl:
                        image = QPixmap()
                        image.loadFromData(self.session.get(url=url).content)
                        self.reqImageUrlList.append(image)
                    self.bottleFindSin.emit(self.reqImageUrlList, self.bottleName, self.bottleLabel, self.bottlePrice)
                    self.findSin = False
                    end = time.time()
                    print("请求时间为", end - start)
                else:
                    time.sleep(0.5)

            except Exception as ex:
                print("BottleFindThread -> run :", ex)


"""
    识别窗口线程、显示视频流等
"""


class BottleIdentifyThread(QThread):
    identifySin = pyqtSignal()

    def __init__(self, parent=None):
        super(BottleIdentifyThread, self).__init__(parent)
        try:
            # 摄像头初始化
            self.cap = cv.VideoCapture()
            self.playLabel = QLabel()
            self.resultTableWidget = QTableWidget()
            self.cue = QLabel()

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
        except Exception as ex:
            print("BottleIdentifyThread -> init :", ex)

    # 线程主体
    def run(self):
        try:
            self.cap = cv.VideoCapture(0)
            self.cue.setText("启动成功,请将瓶子放至识别区!")
            while True:
                if self.playVideo:
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
                        showImage = QImage(self.image, self.image.shape[1], self.image.shape[0], QImage.Format_RGB888)
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
                            variance = round(np.var(self.mseList), 3)
                            average = round(np.mean(self.mseList), 3)

                            print(variance, average)

                            if variance > 10000 and average > 500:
                                self.frequency += 1
                                cv.imwrite("../img/image{}.png".format(self.length), self.image)
                                print("image success write")
                            elif variance < 5000 and variance < 500 and self.frequency >= 2:
                                print("start identifying")
                                self.identifySin.emit()
                                self.frequency = 0
                if self.playVideo is False:
                    self.cap.release()

        except Exception as ex:
            print("BottleIdentifyThread -> run :", ex)


"""
    识别窗口线程,访问识别数据
"""


class GetBottleIdentifyResultThread(QThread):
    getIdentifyResult = pyqtSignal(object, object, object, object)

    def __init__(self, parent=None):
        super(GetBottleIdentifyResultThread, self).__init__(parent)

        self.identifyLike = None
        self.identifyStart = False

    def run(self):
        try:
            self.identifyLike = IdentifyUtil()
            while self.identifyStart:
                bottleName, bottleLabel, bottlePrice, bottleSimilarity = self.identifyLike.resultAnalysis()
                self.getIdentifyResult.emit(bottleName, bottleLabel, bottlePrice, bottleSimilarity)
                self.identifyStart = False
            time.sleep(0.5)
        except Exception as ex:
            print("GetBottleIdentifyResultThread -> run :", ex)


"""
    插入数据线程,防止界面卡顿`
"""


class InsertDataThread(QThread):

    def __init__(self, parent=None):
        super(InsertDataThread, self).__init__(parent)
        self.openId = None
        self.label = None
        self.name = None
        self.price = None

        try:
            self.dbLink = DBUtilClass()
        except Exception as ex:
            try:
                self.dbLink = DBUtilClass()
            except Exception as ex:
                print("InsertDataThread -> DBUtilClass :", ex)
        self.insertDataSin = False

    def run(self):
        try:
            while True:
                if self.insertDataSin:
                    self.setIdentificationData(self.label, self.name, self.price, self.openId)
                    self.insertDataSin = False
                    print("数据插入成功")
                else:
                    time.sleep(0.5)
        except Exception as e:
            print("InsertDataThread-run ->", e)

    def setIdentificationData(self, label, name, price, openId):
        try:
            print(label, name, price, openId)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            userId = self.dbLink.select_one("SELECT userId FROM user_db WHERE `openId`=%s", [openId])["userId"]
            self.dbLink.insert("INSERT INTO IdentifyingInformation(`label`,`name`,`price`,`date`,`user`) VALUES(%s,%s,"
                               "%s,%s,%s)", [label, name, price, date, userId])
            self.dbLink.update("UPDATE user_db SET `total`=`total`+%s WHERE `openId`=%s", [price, openId])
        except Exception as e:
            print("InsertDataThread -> setIdentificationData ->", e)


"""
    启动舵机
"""


class ServoThread(QThread):

    def __init__(self, parent=None):
        super(ServoThread, self).__init__(parent)
        try:
            self.startServo = False
            self.servo = Servo()
        except Exception as e:
            print("ServoThread -> init :", e)

    def run(self):
        while True:
            try:
                if self.startServo:
                    print("servo")
                    self.servo.startServo()
                    self.startServo = False
                time.sleep(0.5)
            except Exception as e:
                print("ServoThread -> init :", e)
