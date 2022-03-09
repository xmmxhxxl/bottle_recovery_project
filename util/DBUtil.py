# -*- codeing = utf-8 -*-
# @Time : 2021/10/3 16:04
# @Author : liman
# @File : mysqlProject.py
# @Software : PyCharm
import pymysql
from sshtunnel import SSHTunnelForwarder


class DBUtilClass:
    def __init__(self):
        self.ssh_host = "120.24.222.48"
        self.ssh_port = 22
        self.ssh_user = "root"
        self.ssh_password = "Xmmxhxxl0512"
        self.mysql_host = "127.0.0.1"
        self.mysql_port = 3306
        self.mysql_user = "root"
        self.mysql_password = "root"
        self.mysql_db = "Identification_Information"
        self.server = None
        self.conn = None
        self.cursor = None

    # 链接对象
    def connect(self):
        self.server = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_password=self.ssh_password,
            remote_bind_address=(self.mysql_host, self.mysql_port))
        self.server.start()
        self.conn = pymysql.connect(host=self.mysql_host,
                                    port=self.server.local_bind_port,
                                    user=self.mysql_user,
                                    passwd=self.mysql_password,
                                    db=self.mysql_db)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        # self.cursor = self.conn.cursor()

    # 关闭链接
    def close(self):
        self.cursor.close()
        self.conn.close()
        self.server.close()

    def select_one(self, sql, params):
        result = ()
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            self.close()
        except Exception as ex:
            print("查询数据失败", ex)
        return result

    # 查询所有数据
    def select_all(self, sql):
        try:
            self.connect()
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.conn.commit()
            self.close()
        except Exception as ex:
            print(ex)
        return result

    def _edit(self, sql, params):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql, params)
            self.conn.commit()
            self.close()
        except Exception as ex:
            print(ex)
        return count

    # 增
    def insert(self, sql, params):
        return self._edit(sql, params)

    # 删
    def delete(self, sql, params):
        return self._edit(sql, params)

    # 改
    def update(self, sql, params):
        return self._edit(sql, params)


# if __name__ == '__main__':
#     mysql = DBUtilClass()
#     # print(mysql.select_one("SELECT total FROM user_db WHERE `openId`=%s", ['oW-4T5CiZ5Z6FSt7AuKY2b-gDLsY']))
#     data = mysql.select_all("SELECT * FROM bottleInformation")
#     # print(data)
#     bottleName = []
#     bottleLabel = []
#     bottlePrice = []
#     bottleImageUrl = []
#     for item in data:
#         bottleImageUrl.append(item["imageUrl"])
#         bottleName.append(item["bottleName"])
#         bottleLabel.append(item["bottleLabel"])
#         bottlePrice.append(item["bottlePrice"])
#     print(bottleLabel)