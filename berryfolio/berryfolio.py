# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
from utils import make_dirs
import sqlite3
import dbOperation
from flask import Flask, render_template, g
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


# 我也不知道为什么，总之这句必须有
app = Flask(__name__)
app.config.from_object(__name__)  # load config from this file , berryfolio.py
# 加载默认配置
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'berryfolio.db'),
    SECRET_KEY='Thisismykeyafuibsvseibgf',
    USERNAME='DAM',
    PASSWORD='passworddam2017',
    UPLOADED_PHOTOS_DEST=os.path.join(os.path.abspath("."), "data")
))
make_dirs([app.config['UPLOADED_PHOTOS_DEST']])

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


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
