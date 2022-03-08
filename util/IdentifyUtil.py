# -*- coding = utf-8 -*-
# @Time : 2021/8/11 14:54
# @Author : 黎满
# @File : IdentifyUtil.py
# @Software : PyCharm
import requests as re
from DBUtil import DBUtilClass

"""
    获取识别数据
"""


class IdentifyUtil:
    def __init__(self):
        super(IdentifyUtil, self).__init__()

        self.bottleLabel = []
        self.bottleName = []
        self.bottlePrice = {}

        self.mysql = DBUtilClass()
        self.kindList = self.mysql.select_all("select * from bottleInformation")
        print(self.kindList)
        self.findKind()

    def findKind(self):
        for i in self.kindList:
            self.bottleLabel.append(i["bottleLabel"])
            self.bottleName.append(i["bottleName"])
            self.bottlePrice.update({i["bottleLabel"]: i["bottleName"]})

    # 请求、处理数据
    def resultAnalysis(self):
        try:
            # 打开文件
            with open(r'../img/image2.png', 'rb') as data:
                imageData = data.read()
                try:
                    result = re.post('http://192.168.137.254:24401/', params={'threshold': 0.1}, data=imageData).json()
                except re.exceptions.ConnectionError:
                    try:
                        result = re.post('http://192.168.137.254:24401/', params={'threshold': 0.1},
                                         data=imageData).json()
                    except re.exceptions.ConnectionError:
                        try:
                            result = re.post('http://192.168.137.254:24401/', params={'threshold': 0.1},
                                             data=imageData).json()
                        except Exception as e:
                            print("请求识别结果失败: IdentifyUtil -> resultAnalysis", e)

            result = tuple(result["results"])[0]
            label = result['label']
            similarity = round(result["score"] * 100, 2)

            for self.item in self.bottleLabel:
                if similarity < 70:
                    return None, None

                if label == self.item and similarity > 90:
                    bottleName = self.bottleName[self.bottleLabel.index(self.item)]
                    price = self.bottlePrice[label]
                    print(label, similarity, price, bottleName)

                    return bottleName, price
        except Exception as ex:
            print("IdentifyUtil -> resultAnalysis ->", ex)


if __name__ == '__main__':
    indef = IdentifyUtil()
    bottle, price = indef.resultAnalysis()
    print(bottle, price)
