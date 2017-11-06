# -*- coding: utf-8 -*-
# 在这里写一些测试用的Python语句，与项目无关
import os
import zipfile
import config


def zip(folder):
    """
    对folder下的目录和文件压缩
    :param folder: 输入的folder
    :return: 成功则返回压缩文件的路径，否则返回None
    """
    username = folder.split('/')[-1]
    zip_path = os.path.join(config.GLOBAL['TEMP_PATH'], username + ".zip")
    z = zipfile.ZipFile(zip_path, "w")
    for path, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(path, file)
            file_path_in_zip = os.path.join(path, file).split(folder + os.sep)[-1]
            print file_path
            print file_path_in_zip
            z.write(file_path, file_path_in_zip)
    z.close()
    return zip_path


if __name__ == '__main__':
    print zip("data/Yunzhe")
