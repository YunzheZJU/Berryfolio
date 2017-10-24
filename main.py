# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
from utils import make_dirs
import dbOperation
from flask import Flask, request, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


# 我也不知道为什么，总之这句必须有
app = Flask(__name__)
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.path.abspath("."), "data")  # 文件储存地址
make_dirs([app.config['UPLOADED_PHOTOS_DEST']])

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB


html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=photo>
         <input type=submit value=上传>
    </form>
    '''


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        file_url = photos.url(filename)
        return html + '<br><img src=' + file_url + '>'
    return html


# # 这是通往网站首页的大门
# @app.route('/', methods=['GET'])
# def home():
#     return render_template('home.html'), 200, {'Cache-Control': 'no-cache'}
