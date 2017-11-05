# -*- coding: utf-8 -*-
# 在这里写一些测试用的Python语句，与项目无关
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
    return "".join(char), image_path


if __name__ == '__main__':
    print generate_verify_code("")
