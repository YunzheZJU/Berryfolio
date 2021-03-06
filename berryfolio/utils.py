# -*- coding: utf-8 -*-
import os
import shutil
import config
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from logger import logger


def encode_color(s, w):
    return ((w & 192) >> 6) + (s & 252)


def decode_color(s):
    return (s & 3) << 6


# 随机字母:
def rnd_char():
    return chr(random.randint(65, 90))


# 随机颜色1:
def rnd_color():
    return random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)


# 随机颜色2:
def rnd_color2():
    return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)


def remove_tree(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def make_dir(path, clean=0):
    if clean:
        remove_tree(path)
    if not os.path.exists(path):
        os.mkdir(path)


def add_data_path_prefix(path):
    """
    为路径套上前缀路径，前缀到data/为止
    :param path: 用户目录物理路径，应以用户名开头，形如"Yunzhe/rootg"
    :return: 结果路径，形如"/home/pi/data/Yunzhe/rootg"
    """
    return os.path.join(config.GLOBAL['DATA_PATH'], path)


def remove_data_path_prefix(path):
    """
    为路径去掉前缀路径，前缀到data/为止
    :param path: 用户目录物理路径，应以用户名开头，形如"e:\projects\pycharm\dams\berryfolio\data\1\1\3\source1.jpg"
    :return: 结果路径，形如"1/1/3/source1.jpg
    """
    return path.replace(config.GLOBAL['DATA_PATH'] + os.path.sep, "").replace(os.path.sep, "/")


def remove_root_path_prefix(path):
    """
    为路径去掉前缀路径，前缀到berryfolio/为止
    :param path: 用户目录物理路径，应以用户名开头，形如"e:\projects\pycharm\dams\berryfolio\data\1\1\3\source1.jpg"
    :return: 结果路径，形如"/data/1/1/3/source1.jpg
    """
    return path.replace(config.GLOBAL['ROOT_PATH'], "").replace(os.path.sep, "/")


def make_user_dir(uid):
    """
    在data/目录下建立用户文件夹
    :param uid: 用户名
    :return: 成功则返回用户文件夹的绝对路径，否则返回None
    """
    try:
        user_dir = add_data_path_prefix(str(uid))
        make_dir(user_dir, clean=1)
        return user_dir
    except IOError:
        return None


def make_user_sub_dir(uid, parent, did):
    """
    在parent文件夹下创建子文件夹
    :param uid: 用户ID
    :param parent: 父目录路径，相对用户文件夹的路径
    :param did: 新目录ID
    :return: 成功则返回子目录的绝对路径，否则返回None
    """
    try:
        path = os.path.join(str(uid), parent) if parent else str(uid)
        sub_dir = os.path.join(add_data_path_prefix(path), str(did))
        make_dir(sub_dir)
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
        draw.text((width / 4 * t + 10, 0), char[-1], font=font, fill=rnd_color2())
    # 模糊:
    image = image.filter(ImageFilter.BLUR)
    image_path = os.path.join('images', 'generate', 'vcode.jpg')
    image.save(os.path.join(config.GLOBAL['STATIC_PATH'], image_path))
    return "".join(char), image_path.replace("\\", "/")


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
    config.GLOBAL['TEMP_PATH'] = os.path.join(root_path, 'temp')
    config.GLOBAL['WM_PATH'] = os.path.join(root_path, 'static', 'images', 'wm.jpg')
    return 1


def make_dict(file_info):
    """
    将传入的文件信息元组转换为字典：文件名（可能为unicode）、描述（可能为空）、存储路径等
    :param file_info: 存储文件信息的元组，形如(1, u'123', u'hahahah', 3,
        u'e:\projects\pycharm\dams\berryfolio\data\1\1\3\source1.jpg', 1, "JPEG", 750, 445)
    :return: 存储文件关键信息的字典，形如{'status': 'success', 'fid': 1, 'title': u'123', 'description': u'hahahah',
        'pid': 3, 'path': u'e:\projects\pycharm\dams\berryfolio\data\1\1\3\source1.jpg', 'uid': 1, 'format': 'JPEG',
        'width': 750, 'height': 445}
    """
    return {'status': 'success', 'fid': file_info[0], 'title': file_info[1],
            'description': file_info[2] if file_info[2] else '', 'pid': file_info[3],
            'path': file_info[4], 'uid': file_info[5], 'format': file_info[6],
            'width': file_info[7], 'height': file_info[8], 'date': file_info[9],
            'tag_1': file_info[10], 'tag_2': file_info[11], 'tag_3': file_info[12]}


def make_zip(db, path_to_folder, name):  # FIXME
    """
    对folder下的目录和文件压缩
    :param db: 数据库操作对象
    :param path_to_folder: 输入的folder，相对路径或绝对路径
    :param name: 压缩文件名
    :return: 成功则返回压缩文件名，否则返回None
    """
    try:
        folder = path_to_folder.split(os.sep)[-1]
        folder_name = db.get_name(int(folder), 1)
        folder_zip = os.path.join(config.GLOBAL['TEMP_PATH'], "zip")
        folder_copy = os.path.join(folder_zip, folder)
        for path, dirs, files in os.walk(folder_zip):
            for d in dirs:
                remove_tree(os.path.join(path, d))
        shutil.copytree(path_to_folder, folder_copy)
        for path, dirs, files in os.walk(folder_copy, topdown=False):
            for f in files:
                file_path = os.path.join(path, f)
                os.rename(file_path, os.path.join(path, db.search_file_by_filename(f) + "." + f.split(".")[-1]))
            for d in dirs:
                os.rename(os.path.join(path, d), os.path.join(path, db.get_name(int(d), 1)))
        os.rename(folder_copy, os.path.join(folder_zip, folder_name))
        shutil.make_archive(os.path.join(config.GLOBAL['TEMP_PATH'], name), "zip", folder_zip, folder_name)
        return name + ".zip"
    except StandardError as ex:
        logger.error(ex.message)
        return None


def add_watermark(src, dst, wm):
    try:
        filename = src.split("\\")[-1].split(".")[0]
        path_png = os.path.join(config.GLOBAL['TEMP_PATH'], filename + "_converted.png")
        # Convert the source image to PNG RGBA and save it
        s_img = Image.open(src)
        fm = s_img.format
        s_img.save(path_png)
        s_img.close()
        # Open the converted png image and load pixel info
        s_img = Image.open(path_png).convert("RGB")
        s_p = s_img.load()
        w, h = s_img.size
        # Open the watermark image and resize it
        w_img = Image.open(wm)
        w_p = w_img.resize((w, h)).load()
        # Create an image for storing results
        d_img = Image.new("RGB", (w, h))
        d_p = d_img.load()
        for x in range(w):
            for y in range(h):
                (rw, gw, bw) = w_p[x, y]
                (rs, gs, bs) = s_p[x, y]
                rd = encode_color(rs, rw)
                gd = encode_color(gs, gw)
                bd = encode_color(bs, bw)
                d_p[x, y] = (rd, gd, bd)
                # exit(0)
        # Save the result
        d_img.save(dst)
        # Close the files.
        s_img.close()
        w_img.close()
        d_img.close()
        return [fm, w, h]
    except StandardError as ex:
        logger.error("Error occurred during watermarking: " + ex.message)
        return None, None, None


def get_file_info(file_info):
    if file_info['status'] == 'success':
        return file_info['title'], file_info['description'], \
               os.path.join("", "data", remove_data_path_prefix(file_info['path'])).decode('utf-8')
    # 否则返回缺省图片
    return u"My Portfolio", u"No description", u'/static/images/wm.jpg'


def resize_avatar(src, dst):
    img = Image.open(os.path.join(config.GLOBAL['TEMP_PATH'], src))
    size = 150, 150
    img.thumbnail(size)
    img.save(os.path.join(config.GLOBAL['STATIC_PATH'], dst))
