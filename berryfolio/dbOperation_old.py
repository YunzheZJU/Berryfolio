# -*- coding: utf-8 -*-
# 在这里写数据库相关函数，会被main.py导入
import sqlite3
from config import DB_PATH
from logger import logger
from utils import Dict
import threading, functools


class _DbCntn(threading.local):
    def __init__(self):
        self.connection = None

    def connect(self):
        logger.info("Openning database...")
        self.connection = sqlite3.connect(DB_PATH)

    def cursor(self):
        logger.info("Getting cursor...")
        return self.connection.cursor()

    def close(self):
        logger.info("Closing database...")
        self.connection.close()


_dbCntn = _DbCntn()


class _ConnectionCtx:
    def __enter__(self):
        # 为_dbCntn建立连接
        logger.info("Establishing connection...")
        global _dbCntn
        _dbCntn.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 释放连接
        logger.info("Releasing connection...")
        global _dbCntn
        _dbCntn.close()

def with_connection(func):
    """
    Decorator for reuse connection.

    @with_connection
    def foo(*args, **kw):
        f1()
        f2()
        f3()
    """
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
    return _wrapper


@with_connection
def select(sql, select_first, *args):
    global _dbCntn
    sql = sql.replace('?', '%s')
    logger.info('SQL: %s, ARGS: %s' % (sql, args))
    cursor = _dbCntn.cursor()
    cursor.execute(sql, args)
    result = None
    if cursor.description:
        names = [x[0] for x in cursor.description]
        if select_first:
            value = cursor.fetchone()
            if value:
                result =  Dict(names, value)
        else:
            result = [Dict(names, x) for x in cursor.fetchall()]
    return result


def insert(table, **kwargs):



def update(sql, *args):



if __name__ == '__main__':
    logger.info("Testing dbOperation")


