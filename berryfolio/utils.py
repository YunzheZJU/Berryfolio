# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random


# 随机字母:
def rnd_char():
    return chr(random.randint(65, 90))


# 随机颜色1:
def rnd_color():
    return random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)


# 随机颜色2:
def rnd_color2():
    return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)


def make_dirs(paths, clean=0):
    for path in paths:
        if clean:
            if os.path.exists(path):
                os.removedirs(path)
        if not os.path.exists(path):
            os.mkdir(path)


def make_user_dir(root_path, username):
    user_dir = os.path.join(root_path, "static", "data", username)
    make_dirs([user_dir], clean=1)


def make_sub_dir(rootpath, parent, name):
    sub_dir = os.path.join(rootpath, parent, name)
    make_dirs([sub_dir])


def get_parent_path(db, currentpath, dirID):
    parentID = db.get_parent_id(dirID)
    if parentID:
        parentname = db.get_dir_name(dirID)
        currentpath = os.path.join(parentname, currentpath)
        get_parent_path(db, currentpath, parentID)
    else:
        return currentpath


def generate_tree(db, nodeID):
    """
    递归构造节点树，囊括所有目录
    :param db: 数据库操作对象
    :param nodeID: 节点ID
    :return: 节点，形如{1: ['root', {}]}
    """
    childrenID = db.get_children(nodeID)
    dir_type = childrenID[0]
    if dir_type == 1:
        node = {nodeID: [db.get_dir_name(nodeID), {}]}
        for childID in childrenID[1:]:
            node[nodeID][1][childID] = [db.get_dir_name(nodeID), generate_tree(db, childID)]
        return node
    elif dir_type == 2:
        return {}


def generate_verify_code(root_path):
    # 240 x 60:
    width = 60 * 4
    height = 60
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    font = ImageFont.truetype(os.path.join(root_path, 'static', 'fonts', 'Arial.ttf'), 36)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 存储结果字符
    char = []
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rnd_color())
    # 输出文字:
    for t in range(4):
        char.append(rnd_char())
        draw.text((60 * t + 10, 10), char[-1], font=font, fill=rnd_color2())
    # 模糊:
    image = image.filter(ImageFilter.BLUR)
    image_path = os.path.join('images', 'generate', 'code.jpg')
    image.save(os.path.join(root_path, 'static', image_path))
    return char, image_path


class Dict(dict):
    """
    Simple dict but support access as x.y style.

    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    >>> d1.y = 200
    >>> d1['y']
    200
    >>> d2 = Dict(a=1, b=2, c='3')
    >>> d2.c
    '3'
    >>> d2['empty']
    Traceback (most recent call last):
        ...
    KeyError: 'empty'
    >>> d2.empty
    Traceback (most recent call last):
        ...
    AttributeError: 'Dict' object has no attribute 'empty'
    >>> d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
    >>> d3.a
    1
    >>> d3.b
    2
    >>> d3.c
    3
    """
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
