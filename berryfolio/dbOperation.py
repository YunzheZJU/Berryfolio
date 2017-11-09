# -*- coding: utf-8 -*-
# 在这里写数据库相关函数，会被main.py导入
import sqlite3
from os.path import join
import config
from logger import logger
from utils import extract_file_info


class DbConnect:
    def __init__(self):
        self.db = None
        try:
            # 打开数据库连接
            logger.info("Connecting to database...")
            self.db = sqlite3.connect(config.GLOBAL['DB_PATH'])
        except Exception as ex:
            logger.error("Fail to connect to database: " + ex.message)
            # raise Exception("Fail to connect to database: " + ex.__str__())

    def __del__(self):
        try:
            # 关闭数据库连接
            logger.info("Closing database connection...")
            self.db.close()
        except Exception as ex:
            logger.error("Fail to close database: " + ex.message)
            # raise Exception("Fail to close database: " + ex.__str__())

    def _query(self, sql):
        try:
            logger.info("Querying sql: " + sql + "...")
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
            logger.info("Executing sql: " + sql + "...")
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
        sql = "INSERT INTO User (username, password) VALUES ('%s', '%s')" % (username, password)
        if self._execute(sql):
            return username
        return None

    # Function 2: Log in
    def match_user_pw(self, username, password):
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: 匹配则返回1，否则返回0
        """
        sql = "SELECT * FROM User WHERE username = '%s' AND password = '%s'" % (username, password)
        results = self._query(sql)
        if results:
            return 1
        return 0

    # Function 3: Check username
    def check_username(self, username):
        """
        检查用户名是否注册过
        :param username: 需要检查的用户名
        :return: 存在则返回1，否则返回0
        """
        sql = "SELECT * FROM User WHERE username = '%s'" % username
        results = self._query(sql)
        if results:
            return 1
        return 0

    # Function 4: Add dictionary
    def add_directory(self, name, dir_type, pid, user):
        """
        添加一条目录信息，目录ID自增
        :param name: 目录的显示名
        :param dir_type: 目录的类型（具有子目录，为1；或不具有子目录，为2）
        :param pid: 父目录的ID（根目录时为None）
        :param user: 目录所属用户名
        :return: 成功则返回目录ID，否则返回None
        """
        sql = "INSERT INTO Directory (name, type, user) VALUES ('%s', %d, '%s')" \
              % (name, dir_type, user)
        if self._execute(sql):
            sql = "SELECT last_insert_ROWID() FROM Directory"
            results = self._query(sql)
            if results:
                rowid = results[0][0]
                if pid:
                    sql = "UPDATE Directory SET parentID = %d WHERE ROWID = %d" % (pid, rowid)
                    if self._execute(sql):
                        return rowid
                else:
                    return rowid
        return 0

    # Function 5: Add file
    def add_file(self, pid, filename, description, file_path, username):
        """
        添加一条文件信息，文件ID自增
        :param pid: 存放文件的目录的ID
        :param filename: 文件名
        :param description: 描述
        :param file_path: 文件存放路径
        :param username: 文件所属用户
        :return: 成功则返回文件ID，否则返回None
        """
        sql = "INSERT INTO File (name, parentID, path, user) VALUES ('%s', %d, '%s', '%s')" \
              % (filename, pid, file_path, username)
        if self._execute(sql):
            sql = "SELECT last_insert_ROWID() FROM File"
            results = self._query(sql)
            if results:
                rowid = results[0][0]
                if description:
                    sql = "UPDATE File SET description = '%s' WHERE ROWID = %d" % (description, rowid)
                    if self._execute(sql):
                        return rowid
                else:
                    return rowid
        return 0

    # Function 6: Get children of a directory
    def get_dir_children(self, did):
        """
        获得目录下的所有子目录ID或文件ID
        :param did: 需要索引的父目录ID
        :return: 成功则返回list，存储所有子目录ID或文件ID，其中list的第一个元素标志其后的ID为目录ID（1）还是文件ID（2）
            ，否则返回None
        """
        dir_type = self.get_dir_type(did)
        sql = ""
        if dir_type == 1:
            sql = "SELECT ROWID FROM Directory WHERE parentID = %d" % did
        elif dir_type == 2:
            sql = "SELECT ROWID FROM File WHERE parentID = %d" % did
        results = self._query(sql)
        if results:
            results = [dir_type] + map(lambda tp: tp[0], results)
            return results
        return None

    # Function 7: Get root directory
    def get_dir_root(self, username):
        """
        根据用户名获得用户的根目录ID
        :param username: 用户名
        :return: 成功则返回目录ID，否则返回None
        """
        sql = "SELECT ROWID FROM Directory WHERE user = '%s' AND parentID ISNULL " % username
        results = self._query(sql)
        if results:
            return results[0][0]
        return None

    # Function 8: Get type of directory
    def get_dir_type(self, did):
        """
        根据目录ID获取目录类型
        :param did: 目录ID
        :return: 成功则返回目录类型，否则返回None
        """
        sql = "SELECT type FROM Directory WHERE ROWID = %d" % did
        results = self._query(sql)
        if results:
            return results[0][0]
        return 0

    # Function 9: Get directory ID where type == 1
    def get_dirs_by_user(self, username, rtype=1):
        """
        获取某用户的所有指定类型的目录ID，
        :param username: 用户名
        :param rtype: 目录类型，1或2，默认为1
        :return: 成功则返回list，存储所有目录ID，否则返回None
        """
        sql = "SELECT ROWID FROM Directory WHERE user = '%s' AND type = %d " % (username, rtype)
        results = self._query(sql)
        if results:
            results = map(lambda tp: tp[0], results)
            return results
        return None

    # Function 10: Get path of file
    def get_file_path(self, fid):
        """
        获得文件的存储路径
        :param fid: 文件ID
        :return: 成功则返回文件的存储路径，形如"Yunzhe/root/folder/1.jpg"，否则返回None
        """
        sql = "SELECT path FROM File WHERE ROWID = %d" % fid
        results = self._query(sql)
        if results:
            return results[0][0].encode('utf-8')
        return None

    # Function 11: Get details a file
    def get_file_info(self, fid):
        """
        获得文件的详细信息
        :param fid: 文件ID
        :return: 返回dict，依次存储状态码（success或者failed，若为failed则无需后面字段）、文件名、描述、存储路径
        """
        sql = "SELECT * FROM File WHERE ROWID = %d" % fid
        results = self._query(sql)
        if results:
            results = extract_file_info(results[0])
            return results
        return {'status': 'failed'}

    # Function 12: Get all files of a user
    def get_files_by_user(self, username):
        """
        获取用户上传的所有文件
        :param username: 用户名
        :return: 成功则返回list，存储所有文件ID，否则返回None
        """
        sql = "SELECT ROWID FROM File WHERE user = '%s'" % username
        results = self._query(sql)
        if results is not None:
            results = map(lambda tp: tp[0], results)
            return results
        return None

    # Function 13: Update file
    def update_file_info(self, fid, pid, filename, description, file_path):
        """
        更新文件信息
        :param fid: 文件ID
        :param pid: 父目录ID
        :param filename: 文件名
        :param description: 描述
        :param file_path: 文件存储路径，形如"Yunzhe/root/folder/1.jpg"
        :return: 成功则返回1，否则返回0
        """
        sql = "UPDATE File SET parentID = %d, name = '%s', path = '%s' WHERE ROWID = %d" \
              % (pid, filename, file_path, fid)
        if self._execute(sql):
            if description:
                sql = "UPDATE File SET description = '%s' WHERE ROWID = %d" % (description, fid)
            else:
                sql = "UPDATE File SET description = NULL WHERE ROWID = %d" % fid
            if self._execute(sql):
                return 1
        return 0

    # Function 14: Get parent directory
    def get_parent_id(self, rid, rtype):
        """
        获得父目录的ID
        :param rid: 请求的ID
        :param rtype: 传入ID的类型，目录ID为1，文件ID为2
        :return: 成功则返回父目录ID（无父目录时返回None），否则返回None
        """
        sql = ""
        if rtype == 1:
            sql = "SELECT parentID FROM Directory WHERE ROWID = %d" % rid
        elif rtype == 2:
            sql = "SELECT parentID FROM File WHERE ROWID = %d" % rid
        results = self._query(sql)
        if results:
            return results[0][0]
        return None

    # Function 15: Get name of a directory or file
    def get_name(self, rid, rtype):
        """
        根据ID获得name
        :param rid: 请求的ID
        :param rtype: 传入ID的类型，目录ID为1，文件ID为2
        :return: 成功则返回name，否则返回None
        """
        sql = ""
        if rtype == 1:
            sql = "SELECT name FROM Directory WHERE ROWID = %d" % rid
        elif rtype == 2:
            sql = "SELECT name FROM File WHERE ROWID = %d" % rid
        results = self._query(sql)
        if results:
            return results[0][0].encode('utf-8')
        return None

    # Function 16: Generate parent path of dir
    def gen_parent_path(self, current_path=None, dir_id=None):
        """
        获得请求的目录ID的路径（不包含自身）
        :param current_path: 递归时时用到的当前路径
        :param dir_id: 请求的目录ID
        :return: 从根目录到该目录的路径（不包含该目录），形如"root\\folder\\sub"
        """
        pid = self.get_parent_id(dir_id, 1)
        if pid:
            parentname = self.get_name(pid, 1)
            current_path = join(parentname, current_path) if current_path else parentname
            current_path = self.gen_parent_path(current_path, pid)
        return current_path

    # Function 17: Generate directory tree
    def generate_tree(self, nid):
        """
        递归构造节点树，囊括所有目录
        :param nid: 节点ID
        :return: 节点，形如{1: ['root', {2: ['folder', {3: ['sub', {7: ['sud', {}]}]}], 4: ['folder1', {}]}]}
        """
        cids = self.get_dir_children(nid)
        node = {nid: [self.get_name(nid, 1), {}]}
        if cids:
            dir_type = cids[0]
            if dir_type == 1:
                for cid in cids[1:]:
                    node[nid][1] = dict(node[nid][1], **self.generate_tree(cid))
        return node

    # Function 18: Delete file
    def del_file(self, fid):
        """
        删除文件条目
        :param fid: 文件ID
        :return: 成功则返回1，否则返回0
        """
        sql = "DELETE FROM File WHERE id = %d" % fid
        if self._execute(sql):
            return 1
        return 0


if __name__ == '__main__':
    db = DbConnect()
    with open('schema.sql', mode='r') as f:
        db.execute_scripts(f.readlines())
    if 0:
        # F1
        print db.add_user("Yunzhe", "123456")
        # F2
        print db.match_user_pw("Yunzhe", "123456")
        print db.match_user_pw("Yunzhe", "12345")
        print db.match_user_pw("Yunzh", "123456")
        # F3
        print db.check_username("Yunzhe")
        print db.check_username("Y")
        # F4
        print db.add_directory("root", 1, None, "Yunzhe")
        print db.add_directory("folder", 1, 1, "Yunzhe")
        print db.add_directory("sub", 1, 2, "Yunzhe")
        print db.add_directory("folder1", 1, 1, "Yunzhe")
        print db.add_directory("folder2", 1, 1, "Yunzhe")
        print db.add_directory("root", 1, None, "Asaki")
        print db.add_directory("sud", 2, 3, "Yunzhe")
        # F5
        print db.add_file(3, "photo1.jpg", "hahahah", "Yunzhe/root/folder/sub", "Yunzhe")
        print db.add_file(3, "photo1.jpg", None, "Yunzhe/root/folder/sub", "Yunzhe")
        # F6
        print db.get_dir_children(1)
        print db.get_dir_children(2)
        print db.get_dir_children(3)
        # F7
        print db.get_dir_root("Yunzhe")
        print db.get_dir_root("Asaki")
        print db.get_dir_root("A")
        # F8
        print db.get_dir_type(1)
        print db.get_dir_type(2)
        print db.get_dir_type(3)
        print db.get_dir_type(4)
        print db.get_dir_type(5)
        # F9
        print db.get_dirs_by_user("Yunzhe")
        print db.get_dirs_by_user("Yunzhe", 2)
        print db.get_dirs_by_user("Asaki")
        print db.get_dirs_by_user("Asaki", 2)
        # F10
        print db.get_file_path(1)
        print db.get_file_path(2)
        print db.get_file_path(3)
        # F11
        print db.get_file_info(1)
        print db.get_file_info(2)
        print db.get_file_info(3)
        # F12
        print db.get_files_by_user("Yunzhe")
        # F13
        print db.update_file_info(1, 4, "photo", None, "Yunzhe/root/folder/sud")
        print db.update_file_info(1, 3, "photo1.jpg", "hahahah", "Yunzhe/root/folder/sub")
        # F14
        print db.get_parent_id(1, 1)
        print db.get_parent_id(2, 1)
        print db.get_parent_id(3, 1)
        print db.get_parent_id(6, 1)
        print db.get_parent_id(1, 2)
        print db.get_parent_id(3, 2)
        print db.get_parent_id(1, 3)
        # F15
        print db.get_name(1, 1)
        print db.get_name(2, 1)
        print db.get_name(3, 1)
        print db.get_name(6, 1)
        print db.get_name(1, 2)
        print db.get_name(3, 2)
        print db.get_name(6, 3)
        # F16
        print db.gen_parent_path(dir_id=7)
        # F17
        print db.generate_tree(1)
        # F18
        print db.del_file(1)
