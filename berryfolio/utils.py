# -*- coding: utf-8 -*-
import os
import config
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


def add_data_path_prefix(path):
    """
    为路径套上前缀路径，前缀到data/为止
    :param path: 用户目录物理路径，应以用户名开头，形如"Yunzhe/root"
    :return: 结果路径，形如"/home/pi/data/Yunzhe/root"
    """
    return os.path.join(config.GLOBAL['DATA_PATH'], path)


def make_user_dir(username):
    """
    在data/目录下建立用户文件夹
    :param username: 用户名
    :return: 成功则返回用户文件夹的绝对路径，否则返回None
    """
    try:
        user_dir = add_data_path_prefix(username)
        make_dirs([user_dir], clean=1)
        return user_dir
    except IOError:
        return None


def make_user_sub_dir(username, parent, name):
    """
    在parent文件夹下创建子文件夹
    :param username: 用户名
    :param parent: 父目录路径，相对用户文件夹的路径
    :param name: 新文件夹名
    :return: 成功则返回子目录的绝对路径，否则返回None
    """
    try:
        path = os.path.join(username, parent) if parent else username
        sub_dir = os.path.join(add_data_path_prefix(path), name)
        make_dirs([sub_dir])
        return sub_dir
    except IOError:
        return None


def generate_verify_code(width=240, height=40, font_family='Arial.ttf', font_size=36):
    """
    生成4个字符的验证码图片
    :param width: 图片宽度
    :param height: 图片高度
    :param font_family: 字体
    :param font_size: 字号
    :return: 验证码和图片的相对路径，形如('TABD', "images/generate/vcode.jpg)
    """
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    font = ImageFont.truetype(os.path.join(config.GLOBAL['FONT_PATH'], font_family), font_size)
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
        draw.text((width / 4 * t + 10, 10), char[-1], font=font, fill=rnd_color2())
    # 模糊:
    image = image.filter(ImageFilter.BLUR)
    image_path = os.path.join('images', 'generate', 'vcode.jpg')
    image.save(os.path.join(config.GLOBAL['STATIC_PATH'], image_path))
    return char, image_path


def generate_global(root_path):
    """
    根据传入的root_path建立一系列GLOBAL参数，绝对路径
    :param root_path: app.root_path
    :return: 成功则返回1，否则返回0
    """
    config.GLOBAL['ROOT_PATH'] = root_path
    config.GLOBAL['DATA_PATH'] = os.path.join(root_path, "data")
    config.GLOBAL['STATIC_PATH'] = os.path.join(root_path, 'static')
    config.GLOBAL['FONT_PATH'] = os.path.join(root_path, 'static', 'fonts')
    return 1


def extract_file_info(file_info):
    """
    从传入的文件信息元组中提取必要信息：文件名（可能为unicode）、描述（可能为空）、存储路径
    :param file_info: 存储文件信息的元组，形如(1, u'photo1.jpg', u'hahahah', 3, u'Yunzhe/root/folder/sub', u'Yunzhe')
    :return: 存储文件关键信息的字典，形如{'filename': 'photo1.jpg', 'description': 'hahahah', 'path': 'Yunzhe/root/folder/sub'}
    """
    # 将可能存在的unicode元素转换为str
    converted = map(lambda tp: tp.encode('utf-8') if isinstance(tp, unicode) else tp, file_info)
    return {'status': 'success', 'filename': converted[1], 'description': converted[2] if converted[2] else '',
            'path': converted[4]}


# class Dict(dict):
#     """
#     Simple dict but support access as x.y style.
#
#     >>> d1 = Dict()
#     >>> d1['x'] = 100
#     >>> d1.x
#     100
#     >>> d1.y = 200
#     >>> d1['y']
#     200
#     >>> d2 = Dict(a=1, b=2, c='3')
#     >>> d2.c
#     '3'
#     >>> d2['empty']
#     Traceback (most recent call last):
#         ...
#     KeyError: 'empty'
#     >>> d2.empty
#     Traceback (most recent call last):
#         ...
#     AttributeError: 'Dict' object has no attribute 'empty'
#     >>> d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
#     >>> d3.a
#     1
#     >>> d3.b
#     2
#     >>> d3.c
#     3
#     """
#     def __init__(self, names=(), values=(), **kw):
#         super(Dict, self).__init__(**kw)
#         for k, v in zip(names, values):
#             self[k] = v
#
#     def __getattr__(self, key):
#         try:
#             return self[key]
#         except KeyError:
#             raise AttributeError(r"'Dict' object has no attribute '%s'" % key)
#
#     def __setattr__(self, key, value):
#         self[key] = value
