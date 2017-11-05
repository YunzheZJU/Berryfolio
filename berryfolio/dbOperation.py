# -*- coding: utf-8 -*-
# 在这里写数据库相关函数，会被main.py导入
import sqlite3
from config import DB_PATH
from logger import logger


class DbConnect:
    def __init__(self):
        self.db = None
        try:
            # 打开数据库连接
            logger.info("Connecting to database...")
            self.db = sqlite3.connect(DB_PATH)
        except Exception as ex:
            logger.error("Fail to connect to database: " + ex.message)
            # raise Exception("Fail to connect to database: " + ex.__str__())

    def __del__(self):
        try:
            # 关闭数据库连接
            logger.info("Closing database...")
            self.db.close()
        except Exception as ex:
            logger.error("Fail to close database: " + ex.message)
            # raise Exception("Fail to close database: " + ex.__str__())

    def _query(self, sql):
        try:
            logger.info("Querying sql " + sql + "...")
            # 获得数据库指针
            cursor = self.db.cursor()
            # 执行SQL语句
            cursor.execute(sql)
            # 获得查询结果
            results = cursor.fetchall()
            return results
        except Exception as ex:
            logger.error("Unable to query sql: " + sql + ". Exception: " + ex.message)
            # raise Exception("Unable to query sql: " + sql + ". Exception: " + ex.message)
            return None

    def _execute(self, sql):
        try:
            logger.info("Executing sql " + sql + "...")
            # 获得数据库指针
            cursor = self.db.cursor()
            # 执行SQL语句
            cursor.execute(sql)
            # 提交数据库事务
            self.db.commit()
            return 1
        except Exception as ex:
            # 若有错误则回滚操作
            self.db.rollback()
            logger.error("Unable to execute sql: " + sql + ". Exception: " + ex.message)
            # raise Exception("Unable to execute sql: " + sql + ". Exception: " + ex.message)
            return 0

    # Function 0: Execute Scripts
    def execute_scripts(self, scripts):
        try:
            logger.info("Executing scripts ...")
            # 获得数据库指针
            cursor = self.db.cursor()
            for sql in scripts:
                # 执行SQL语句
                cursor.execute(sql)
                # print sql
            # 提交数据库事务
            self.db.commit()
            return 1
        except Exception as ex:
            # 若有错误则回滚操作
            self.db.rollback()
            logger.error("Unable to execute scripts: " + ex.message)
            # raise Exception("Unable to execute scripts: " + ex.message)
            return 0

    # Function 1: Registration
    def register(self, username, password):
        """
        用户注册
        :param username: 用户名（唯一）
        :param password: 密码
        :return: 成功则返回username，否则返回None
        """
        sql = "TODO: Write query language here"
        if self._execute(sql):
            return username
        else:
            return None

    # Function 2: Log in
    def login(self, username, password):
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: 匹配则返回1，否则返回0
        """
        return 1

    # Function 3: Check username
    def check_username(self, username):
        """
        检查用户名是否注册过
        :param username: 需要检查的用户名
        :return: 存在则返回1，否则返回0
        """
        return 1

    # Function 4: Add dictionary
    def add_dictionary(self, name, type, parentID, user):
        """
        添加一条目录信息，目录ID自增
        :param name: 目录的显示名
        :param type: 目录的类型（具有子目录，为1；或不具有子目录，为2）
        :param parentID: 父目录的ID（根目录时为None）
        :param user: 目录所属用户名
        :return: 成功则返回目录ID，否则返回None
        """
        return 1

    # Function 5: Add file
    def add_file(self, parentID, filename, description, filepath):
        """
        添加一条文件信息，文件ID自增
        :param parentID: 存放文件的目录的ID
        :param filename: 文件名
        :param description: 描述
        :param filepath: 文件存放路径
        :return: 成功则返回文件ID，否则返回None
        """
        return 1

    # Function 6: Get directory ID where type == 1
    def get_user_dir_1(self, username):
        """
        获取某用户的所有可创建子目录的目录ID，即目录类型为1
        :param username: 用户名
        :return: 成功则返回list，存储所有目录ID，否则返回None
        """
        return [1, 3, 10]

    # Function 7: Get directory ID where type == 2
    def get_user_dir_2(self, username):
        """
        获取某用户的所有可上传文件的目录ID，即目录类型为2
        :param username: 用户名
        :return: 成功则返回list，存储所有目录ID，否则返回None
        """
        return [2, 4]

    # Function 8: Get all files of a user
    def get_user_files(self, username):
        """
        获取用户上传的所有文件
        :param username: 用户名
        :return: 成功则返回list，存储所有文件ID，否则返回None
        """
        return [1, 2, 3, 4]

    # Function 9: Get path of file
    def get_path(self, fileID):
        """
        获得文件的存储路径
        :param fileID: 文件ID
        :return: 成功则返回文件的存储路径，否则返回None
        """
        return "Yunzhe/root/folder/1.jpg"

    # Function 10: Get children of a directory
    def get_children(self, directoryID):
        """
        获得目录下的所有子目录ID或文件ID
        :param directoryID: 需要索引的父目录ID
        :return: 成功则返回list，存储所有子目录ID或文件ID，其中list的第一个元素标志其后的ID为目录ID（1）还是文件ID（2）
            ，否则返回None
        """
        return [1, 2, 4]

    # Function 11: Get details a file
    def get_file_details(self, fileID):
        """
        获得文件的详细信息
        :param fileID: 文件ID
        :return: 成功则返回list，依次存储文件名、描述、存储路径，否则返回None
        """
        return ['zhaopian', 'miaoshu', 'Yunzhe/root/folder/1.jpg']

    # Function 12: Update file
    def update_file_details(self, fileID, filename, description):
        """
        更新文件信息
        :param fileID: 文件ID
        :param filename: 文件名
        :param description: 描述
        :return: 成功则返回1，否则返回0
        """
        return 1

    # Function 13: Get parent directory
    def get_parent_id(self, directoryID):
        """
        获得父目录的ID
        :param directoryID: 请求的子目录ID
        :return: 成功则返回父目录ID，否则返回None
        """
        return 5

    # Function 14: Get directory name
    def get_dir_name(self, directoryID):
        """
        根据目录ID获得目录名
        :param directoryID: 请求的目录ID
        :return: 成功则返回目录名，否则返回None
        """
        return "folder"

    # Function 15: Get root directory
    def get_root_id(self, username):
        """
        根据用户名获得用户的根目录ID
        :param username: 用户名
        :return: 成功则返回目录ID，否则返回None
        """
        return 1

    # Function 15: Get type of directory
    def get_dir_type(self, directoryID):
        """
        根据目录ID获取目录类型
        :param directoryID: 目录ID
        :return: 成功则返回目录类型，否则返回None
        """
        return 1
