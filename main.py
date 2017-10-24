# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
from utils import make_dirs
import dbOperation
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


# 我也不知道为什么，总之这句必须有
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisismykeyafuibsvseibgf'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.path.abspath("."), "data")  # 文件储存地址
make_dirs([app.config['UPLOADED_PHOTOS_DEST']])

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能上传图片！'),
        FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
    else:
        file_url = None
    return render_template('test.html', form=form, file_url=file_url)


# # 这是通往网站首页的大门
# @app.route('/', methods=['GET'])
# def home():
#     return render_template('home.html'), 200, {'Cache-Control': 'no-cache'}
