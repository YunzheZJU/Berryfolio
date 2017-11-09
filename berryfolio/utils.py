# -*- coding: utf-8 -*-
import os
import config
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import zipfile
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
        draw.text((width / 4 * t + 10, 0), char[-1], font=font, fill=rnd_color2())
    # 模糊:
    print char
    print "".join(char)
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


def make_zip(folder, zipname):
    """
    对folder下的目录和文件压缩
    :param folder: 输入的folder，相对路径或绝对路径
    :param zipname: 压缩文件名
    :return: 成功则返回压缩文件的路径，否则返回None
    """
    z = None
    try:
        zip_path = os.path.join(config.GLOBAL['TEMP_PATH'], zipname)
        z = zipfile.ZipFile(zip_path, "w")
        for path, dirs, files in os.walk(folder):
            for filename in files:
                file_path = os.path.join(path, filename)
                file_path_in_zip = os.path.join(path, filename).split(folder + os.sep)[-1]
                print file_path
                print file_path_in_zip
                z.write(file_path, file_path_in_zip)
        z.close()
        return zip_path
    except StandardError:
        if z:
            z.close()
        return None


def add_watermark(src, dst, wm):
    try:
        filename = src.split("\\")[-1].split(".")[0]
        path_png = os.path.join(config.GLOBAL['TEMP_PATH'], filename + "_converted.png")
        # Convert the source image to PNG RGBA and save it
        s_img = Image.open(src)
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
        # print s_img.format, "%dx%d" % (w, h), s_img.mode
        for x in range(w):
            for y in range(h):
                (rw, gw, bw) = w_p[x, y]
                (rs, gs, bs) = s_p[x, y]
                rd = encode_color(rs, rw)
                gd = encode_color(gs, gw)
                bd = encode_color(bs, bw)
                d_p[x, y] = (rd, gd, bd)
                # print rs, rw, (rw & 248) >> 5, rs & 7, rs & 248
                # exit(0)
        # Save the result
        d_img.save(dst)
        # Close the files.
        s_img.close()
        w_img.close()
        d_img.close()
        return dst
    except StandardError as ex:
        logger.error("Error occurred during watermarking: " + ex.message)
        return None
