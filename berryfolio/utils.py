# -*- coding: utf-8 -*-
import os


def make_dirs(paths):
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)


def check_username(username):
    # TODO: 检查用户名是否在已注册用户列表中
    if username in ['Asaki', 'KenBoNely', 'Oreki', 'Yunzhe']:
        return True
    else:
        return False