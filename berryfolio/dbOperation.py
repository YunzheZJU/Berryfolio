# -*- coding: utf-8 -*-
# 在这里写数据库相关函数，会被main.py导入
import sqlite3
from os.path import join
import config
from logger import logger
from utils import make_dict


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
    def add_user(self, username, password, avatar, introduction, name, description):
        """
        用户注册
        :param username: 用户名（唯一）
        :param password: 密码
        :param avatar: 头像文件保存路径（相对static路径）
        :param introduction: 个人介绍
        :param name: 作品集名称
        :param description: 作品集描述
        :return: 成功则返回uid，否则返回None
        """
        sql = "INSERT INTO User (username, password, avatar, introduction, name, description) " \
              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" \
              % (username, password, avatar, introduction, name, description)
        if self._execute(sql):
            sql = "SELECT last_insert_ROWID() FROM User"
            results = self._query(sql)
            if results:
                rowid = results[0][0]
                return rowid
        return None

    # Function 2: Log in
    def match_user_pw(self, username, password):
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: 匹配则返回uid，否则返回0
        """
        sql = "SELECT ROWID FROM User WHERE username = '%s' AND password = '%s'" % (username, password)
        result = self._query(sql)
        if result:
            return result[0][0]
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

    # Function 21: Get user avatar
    def get_user_avatar(self, uid):
        """
        获得用户头像文件路径
        :param uid: 用户ID
        :return: 成功则返回文件路径，否则返回None
        """
        sql = "SELECT avatar FROM User WHERE ROWID = %s" % uid
        result = self._query(sql)
        if result:
            return result[0][0]
        return None

    # Function 20: Get user info
    def get_user_info(self, uid):
        """
        获得用户信息
        :param uid: 用户ID
        :return: 成功则返回保存用户信息的list，否则返回None
        """
        sql = "SELECT avatar, introduction, name, description FROM User WHERE ROWID = %s" % uid
        result = self._query(sql)
        if result:
            return result[0]
        return None

    # Function 19: Update user info
    def update_user_info(self, uid, avatar, introduction, name, description):
        """
        更新用户信息
        :param uid: 用户ID
        :param avatar: 头像文件路径（相对static/）
        :param introduction: 个人介绍
        :param name: 作品集名称
        :param description: 作品集描述
        :return: 成功则返回1，否则返回0
        """
        sql = "UPDATE User SET avatar = '%s', introduction = '%s', name = '%s', description = '%s' " \
              "WHERE ROWID = %d" \
              % (avatar, introduction, name, description, uid)
        if self._execute(sql):
            return 1
        return 0

    # Function 4: Add dictionary
    def add_directory(self, name, dir_type, pid, uid):
        """
        添加一条目录信息，目录ID自增
        :param name: 目录的显示名
        :param dir_type: 目录的类型（具有子目录，为1；或不具有子目录，为2）
        :param pid: 父目录的ID（根目录时为None）
        :param uid: 目录所属用户ID
        :return: 成功则返回目录ID，否则返回None
        """
        sql = "INSERT INTO Directory (name, type, user) VALUES ('%s', %d, %d)" \
              % (name, dir_type, uid)
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
    def add_file(self, pid, filename, description, file_path, uid, fm, w, h, tag_1, tag_2, tag_3):
        """
        添加一条文件信息，文件ID自增
        :param pid: 存放文件的目录的ID
        :param filename: 文件名
        :param description: 描述
        :param file_path: 文件存放路径
        :param uid: 文件所属用户ID
        :param fm: 图片格式
        :param w: 图片宽度
        :param h: 图片高度
        :param tag_1: 标签1
        :param tag_2: 标签2
        :param tag_3: 标签3
        :return: 成功则返回文件ID，否则返回None
        """
        sql = "INSERT INTO File (title, parentID, path, user, format, width, height, date, tag_1, tag_2, tag_3) " \
              "VALUES ('%s', %d, '%s', %d, '%s', %d, %d, CURRENT_DATE, '%s', '%s', '%s')" \
              % (filename, pid, file_path, uid, fm, w, h, tag_1, tag_2, tag_3)
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
    def get_dir_root(self, uid):
        """
        根据用户名获得用户的根目录ID
        :param uid: 用户ID
        :return: 成功则返回目录ID，否则返回None
        """
        sql = "SELECT ROWID FROM Directory WHERE user = %d AND parentID IS NULL " % uid
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
    def get_dirs_by_user(self, uid, rtype=0):
        """
        获取某用户的所有指定类型的目录ID，
        :param uid: 用户ID
        :param rtype: 目录类型，1或2，默认为0，查询所有目录
        :return: 成功则返回list，存储所有目录ID，否则返回None
        """
        if rtype:
            sql = "SELECT ROWID FROM Directory WHERE user = %d AND type = %d " % (uid, rtype)
        else:
            sql = "SELECT ROWID FROM Directory WHERE user = %d" % uid
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
        :return: 成功则返回文件的存储路径，形如"Yunzhe/rootg/folder/1.jpg"，否则返回None
        """
        sql = "SELECT path FROM File WHERE ROWID = %d" % fid
        results = self._query(sql)
        if results:
            return results[0][0]
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
            results = make_dict(results[0])
            return results
        return {'status': 'failed'}

    # Function 12: Get all files of a user
    def get_files_by_user(self, uid):
        """
        获取用户上传的所有文件
        :param uid: 用户ID
        :return: 成功则返回list，存储所有文件ID，否则返回None
        """
        sql = "SELECT ROWID FROM File WHERE user = %d" % uid
        results = self._query(sql)
        if results is not None:
            results = map(lambda tp: tp[0], results)
            return results
        return None

    # Function 13: Update file
    def update_file_info(self, fid, pid, filename, description, file_path, tag_1, tag_2, tag_3):
        """
        更新文件信息
        :param fid: 文件ID
        :param pid: 父目录ID
        :param filename: 文件名
        :param description: 描述
        :param file_path: 文件存储路径，形如"Yunzhe/rootg/folder/1.jpg"
        :param tag_1: 标签1
        :param tag_2: 标签2
        :param tag_3: 标签3
        :return: 成功则返回1，否则返回0
        """
        sql = "UPDATE File SET parentID = %d, title = '%s', path = '%s', tag_1 = '%s', tag_2 = '%s', tag_3 = '%s' " \
              "WHERE ROWID = %d" % (pid, filename, file_path, tag_1, tag_2, tag_3, fid)
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
        :param rtype: 传入ID的类型，用户为0，目录ID为1，文件ID为2
        :return: 成功则返回name，否则返回None
        """
        sql = ""
        if rtype == 1:
            sql = "SELECT name FROM Directory WHERE ROWID = %d" % rid
        elif rtype == 2:
            sql = "SELECT title FROM File WHERE ROWID = %d" % rid
        elif rtype == 0:
            sql = "SELECT username FROM User WHERE ROWID = %d" % rid
        results = self._query(sql)
        if results:
            return results[0][0] if rtype == 1 else results[0][0].encode('utf-8')
        return None

    # Function 16: Generate parent path of dir
    def gen_parent_path(self, did, current_path=None):
        """
        获得请求的目录ID的路径（包含自身）
        :param current_path: 递归时时用到的当前路径
        :param did: 请求的目录ID
        :return: 从根目录到该目录的路径（包含该目录），形如"1\\4\\6"
        """
        pid = self.get_parent_id(did, 1)
        current_path = join(str(did), current_path) if current_path else str(did)
        if pid:
            return self.gen_parent_path(pid, current_path)
        else:
            return current_path

    # Function 17: Generate directory tree
    def generate_tree(self, nid):  # FIXME
        """
        递归构造节点树，囊括所有目录
        :param nid: 节点ID
        :return: 节点，形如{1: ['rootg', {2: ['folder', {3: ['sub', {7: ['sud', {}]}]}], 4: ['folder1', {}]}]}
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

    # Function 21: Search files
    def search_files(self, keyword):
        """
        查找标签内包含keyword的文件，返回文件id
        :param keyword: 关键词
        :return: 成功则返回文件id组成的list，否则返回None
        """
        sql = "SELECT ROWID FROM File WHERE tag_1 LIKE '%" + keyword + \
              "%' OR tag_2 LIKE '%" + keyword + \
              "%' OR tag_3 LIKE '%" + keyword + \
              "%'"
        results = self._query(sql)
        if results:
            results = map(lambda tp: tp[0], results)
            return results
        return None

    # Function 22: Get file title by path
    def search_file_by_filename(self, filename):
        """
        通过文件路径查询文件标题
        :param filename: 文件名，形如"source1.png"
        :return: 成功则返回文件标题，否则返回None
        """
        sql = "SELECT title FROM File WHERE path LIKE '%" + filename + "'"
        result = self._query(sql)
        if result:
            return result[0][0]
        return None

    # Function 23: Get avatar of a user
    def get_avatar(self, uid):
        """
        获得用户头像路径
        :param uid: 用户id
        :return: 成功则返回用户头像路径，否则返回默认头像路径
        """
        sql = "SELECT avatar FROM User WHERE ROWID = %d" % uid
        result = self._query(sql)
        if result:
            return result[0][0]
        return "/static/images/wm.jpg"


if __name__ == '__main__':
    db = DbConnect()
    if 0:
        with open('schema.sql', mode='r') as f:
            db.execute_scripts(f.readlines())
        # F1
        print db.add_user("Yunzhe", "123456", 'images/avatar.jpg', u'这个人很懒', u'我的作品集', u'这是我的作品集')
        # F2
        print db.match_user_pw("Yunzhe", "123456")
        print db.match_user_pw("Yunzhe", "12345")
        print db.match_user_pw("Yunzh", "123456")
        # F3
        print db.check_username("Yunzhe")
        print db.check_username("Y")
        # F4
        print db.add_directory("rootg", 1, None, "Yunzhe")
        print db.add_directory("folder", 1, 1, "Yunzhe")
        print db.add_directory("sub", 1, 2, "Yunzhe")
        print db.add_directory("folder1", 1, 1, "Yunzhe")
        print db.add_directory("folder2", 1, 1, "Yunzhe")
        print db.add_directory("rootg", 1, None, "Asaki")
        print db.add_directory("sud", 2, 3, "Yunzhe")
        # F5
        print db.add_file(3, "photo1.jpg", "hahahah", "Yunzhe/rootg/folder/sub", "Yunzhe", "PNG", 500, 300)
        print db.add_file(3, "photo1.jpg", None, "Yunzhe/rootg/folder/sub", "Yunzhe", "PNG", 500, 300)
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
        print db.update_file_info(1, 4, "photo", None, "Yunzhe/rootg/folder/sud")
        print db.update_file_info(1, 3, "photo1.jpg", "hahahah", "Yunzhe/rootg/folder/sub")
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
        print db.gen_parent_path(6)
        # F17
        print db.generate_tree(1)
        # F18
        print db.del_file(1)
        # F21
        print db.search_files(u"4")
    print db.search_file_by_filename("e:\\projects\\pycharm\\dams\\berryfolio\\data\\1\\1\\3\\source1.png")
