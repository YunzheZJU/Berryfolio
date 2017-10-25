# -*- coding: utf-8 -*-
import os


def make_dirs(paths):
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)
