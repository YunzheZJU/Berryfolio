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
            self.db = sqlite3.connect(DB_PATH)
        except Exception as ex:
            logger.error("Fail to connect to database: " + ex.message)
            # raise Exception("Fail to connect to database: " + ex.__str__())

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # 关闭数据库连接
            self.db.close()
        except Exception as ex:
            logger.error("Fail to close database: " + ex.message)
            # raise Exception("Fail to close database: " + ex.__str__())

    def _query(self, sql):
        try:
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
            return []

    def _execute(self, sql):
        try:
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
            # 获得数据库指针
            cursor = self.db.cursor()
            for sql in scripts:
                # 执行SQL语句
                cursor.execute(sql)
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
    def registration(self, login_name, full_name, passwords):
        sql = "TODO: Write query language here"
        if self._execute(sql):
            return 1
        else:
            return 0

    # Function 2:

    # Function 3:
