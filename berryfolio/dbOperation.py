# -*- coding: utf-8 -*-
# 在这里写数据库相关函数，会被main.py导入
import sqlite3
from os.path import join
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
    def add_user(self, username, password):
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
    def match_user_pw(self, username, password):
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
    def add_directory(self, name, type, parentID, user):
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

    # Function 6: Get children of a directory
    def get_dir_children(self, directoryID):
        """
        获得目录下的所有子目录ID或文件ID
        :param directoryID: 需要索引的父目录ID
        :return: 成功则返回list，存储所有子目录ID或文件ID，其中list的第一个元素标志其后的ID为目录ID（1）还是文件ID（2）
            ，否则返回None
        """
        return [1, 2, 4]

    # Function 7: Get root directory
    def get_dir_root(self, username):
        """
        根据用户名获得用户的根目录ID
        :param username: 用户名
        :return: 成功则返回目录ID，否则返回None
        """
        return 1

    # Function 8: Get type of directory
    def get_dir_type(self, directoryID):
        """
        根据目录ID获取目录类型
        :param directoryID: 目录ID
        :return: 成功则返回目录类型，否则返回None
        """
        return 1

    # Function 9: Get directory ID where type == 1
    def get_dirs_by_user(self, username, type=1):
        """
        获取某用户的所有指定类型的目录ID，
        :param username: 用户名
        :param type: 目录类型，1或2，默认为1
        :return: 成功则返回list，存储所有目录ID，否则返回None
        """
        return [1, 3, 10]

    # Function 10: Get path of file
    def get_file_path(self, fileID):
        """
        获得文件的存储路径
        :param fileID: 文件ID
        :return: 成功则返回文件的存储路径，形如"Yunzhe/root/folder/1.jpg"，否则返回None
        """
        return "Yunzhe/root/folder/1.jpg"

    # Function 11: Get details a file
    def get_file_info(self, fileID):
        """
        获得文件的详细信息
        :param fileID: 文件ID
        :return: 成功则返回dict，依次存储状态码（success或者failed）、文件名、描述、存储路径，否则返回None
        """
        return {'status': 'success', 'filename': 'zhaopian', 'description': 'miaoshu',
                'filepath': 'Yunzhe/root/folder/1.jpg'}

    # Function 12: Get all files of a user
    def get_files_by_user(self, username):
        """
        获取用户上传的所有文件
        :param username: 用户名
        :return: 成功则返回list，存储所有文件ID，否则返回None
        """
        return [1, 2, 3, 4]

    # Function 13: Update file
    def update_file_info(self, fileID, parentID, filename, description, filepath):
        """
        更新文件信息
        :param fileID: 文件ID
        :param parentID: 文件名
        :param filename: 文件名
        :param description: 描述
        :param filepath: 文件存储路径，形如"Yunzhe/root/folder/1.jpg"
        :return: 成功则返回1，否则返回0
        """
        return 1

    # Function 14: Get parent directory
    def get_parent_id(self, ID, type):
        """
        获得父目录的ID
        :param ID: 请求的ID
        :param type: 传入ID的类型，目录ID为1，文件ID为2
        :return: 成功则返回父目录ID，否则返回None
        """
        return 5

    # Function 15: Get directory name
    def get_name(self, ID, type):
        """
        根据ID获得name
        :param ID: 请求的ID
        :param type: 传入ID的类型，目录ID为1，文件ID为2
        :return: 成功则返回name，否则返回None
        """
        return "folder"

    # Function 16: Generate parent path of dir
    def gen_parent_path(self, currentpath=None, dirID=None):
        """
        获得请求的目录ID的路径（不包含自身）
        :param currentpath: 递归时时用到的当前路径
        :param dirID: 请求的目录ID
        :return: 从根目录到该目录的路径（不包含该目录）
        """
        parentID = self.get_parent_id(dirID, 1)
        if parentID:
            parentname = self.get_name(dirID, 1)
            currentpath = join(parentname, currentpath) if currentpath else parentname
            self.gen_parent_path(currentpath, parentID)
        else:
            return currentpath

    # Function 17: Generate directory tree
    def generate_tree(self, nodeID):
        """
        递归构造节点树，囊括所有目录
        :param nodeID: 节点ID
        :return: 节点，形如{1: ['root', {}]}
        """
        childrenID = self.get_dir_children(nodeID)
        dir_type = childrenID[0]
        if dir_type == 1:
            node = {nodeID: [self.get_name(nodeID, 1), {}]}
            for childID in childrenID[1:]:
                node[nodeID][1] = dict(node[nodeID][1], **self.generate_tree(childID))
                # node[nodeID][1][childID] = [self.get_name(childID, 1), self.generate_tree(childID)]
            return node
        elif dir_type == 2:
            return {}
