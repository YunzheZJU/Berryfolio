# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
from utils import make_dirs
import dbOperation
from flask import Flask, url_for, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# 我也不知道为什么，总之这句必须有
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath("."), "data")
make_dirs([app.config['UPLOAD_FOLDER']])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=上传>
    </form>
    '''


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('uploaded_file', filename=filename)
            return html + '<br><img src=' + file_url + '>'
    return html


# # 这是通往网站首页的大门
# @app.route('/', methods=['GET'])
# def home():
#     return render_template('home.html'), 200, {'Cache-Control': 'no-cache'}
