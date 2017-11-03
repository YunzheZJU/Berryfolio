# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
from utils import make_dirs, check_username
from logger import logger
import sqlite3
import db
from flask import Flask, render_template, g, make_response, json, request, session, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


# 我也不知道为什么，总之这句必须有
app = Flask(__name__)
app.config.from_object(__name__)  # load config from this file, berryfolio.py
# 加载默认配置
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'berryfolio.db'),
    SECRET_KEY='Thisismykeyafuibsvseibgf',
    # USERNAME='DAM',
    # PASSWORD='passworddam2017',
    UPLOADED_PHOTOS_DEST=os.path.join(app.root_path, "data")
))
make_dirs([app.config['UPLOADED_PHOTOS_DEST']])

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB


# def connect_db():
#     """Connects to the specific database."""
#     rv = sqlite3.connect(app.config['DATABASE'])
#     rv.row_factory = sqlite3.Row
#     return rv


def get_db():
    """在本次请求产生的全局变量g中创建一个唯一的数据库操作对象"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = db.DbConnect()
    return g.sqlite_db


def init_db():
    """利用写好的sql脚本初始化数据库"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.execute_scripts(f.readlines())


@app.cli.command('initdb')
def initdb_command():
    """初始化数据库的命令行命令"""
    init_db()
    print('Initialized the database.')


# @app.teardown_appcontext
# def close_db(error):
#     """Closes the database again at the end of the request."""
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能上传图片！'),
        FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')


@app.route('/')
def index():
    db = get_db()
    return "<h1>Hello</h1>"


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
    else:
        file_url = None
    rsp = make_response(render_template('test.html', form=form, file_url=file_url))
    rsp.headers['Cache-Control'] = 'no-cache'
    rsp.set_cookie('username', 'the username')
    return rsp


# 这是通往网站首页的大门
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        if 'username' in session:
            # 检查到这个用户曾经登陆过
            if check_username(session['username']):
                # 这是一个注册了的用户并且已经登录过，去个人主页
                return redirect(url_for('mypage'))
            else:
                # 未注册过的假冒用户，踢掉踢掉
                session.pop('username', None)
        # 返回一个正常的主页
        return render_template('home.html')
    elif request.method == 'POST':
        if request.form['type'] == 'Login':
            # TODO: 验证表单里的用户名密码
            if request.form['username'] == 'Yunzhe' and request.form['password'] == 'Zhang':
                # 登录成功，设置session（flask会以cookie的方式处理）
                session['username'] = request.form['username']
                # 登录成功，去mypage
                return redirect(url_for('mypage'))
            else:
                # 登录失败，滚回home
                return render_template('home.html', message="登录失败，请重试")
        elif request.form['type'] == 'Register':
            # TODO: 获得表单内容，检查并存入数据库，初始化文件夹
            # 注册成功，去主页登录一下
            return render_template('home.html', message="注册成功，请登录")


@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
    if request.method == 'GET':
        if 'username' in session:
            # 检查到已经登录
            if check_username(session['username']):
                # 这是一个注册了的用户，给你看自己的个人主页
                # TODO: 从数据库获取这个用户的个人作品，传入模板
                entity = {'entity_0': '12345', 'entity_1': '54321'}
                username = session['username']
                return render_template('mypage.html', entity=entity, username=username)
            else:
                # 未注册过的假冒用户，踢掉踢掉
                session.pop('username', None)
        # 这个用户没登陆就来个人主页，请回去吧
        return redirect(url_for('home'))
    elif request.method == 'POST':
        # TODO: 获得表单内容，检查并存入数据库，更新用户设置
        # 更新成功
        return render_template('mypage.html', message="用户设置已更新")


@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'GET':
        if 'username' in session:
            # 检查到已经登录
            if check_username(session['username']):
                # 这是一个注册了的用户，给你管理自己的作品集
                # TODO: 从数据库获取这个用户的目录信息，传入模板
                directory = {'directory_0': '12345', 'directory_1': '54321'}
                username = session['username']
                return render_template('portfolio.html', directory=directory, username=username)
            else:
                # 未注册过的假冒用户，踢掉踢掉
                session.pop('username', None)
        # 这个用户没登陆就来个人主页，请回去吧
        return redirect(url_for('home'))
    elif request.method == 'POST':
        if request.form['type'] == 'Photo':
            # TODO: 获取表单内容，存入数据库，保存文件
            return render_template('portfolio.html', message="上传成功")
        elif request.form['type'] == 'Attribute':
            # TODO: 获取表单内容，存入数据库，修改文件属性
            return render_template('portfolio.html', message="修改成功")
        elif request.form['type'] == 'directory':
            # TODO: 获取表单内容，存入数据库，新增目录
            return render_template('portfolio.html', message="增加目录成功")


@app.route('/download', methods=['GET'])
def download():
    if 'fileid' in request.args:
        # 获得file id
        fileid = request.args['fileid']
        # TODO: 构造指向该文件的下载链接
        return url_for(fileid)
    elif 'directoryid' in request.args:
        # 获得directory id
        directoryid = request.args['directoryid']
        # TODO: 生成压缩包
        # TODO: 构造指向该压缩包的下载链接
        return url_for(directoryid)


@app.route('/query', methods=['GET'])
def query():
    if 'fileid' in request.args:
        # 获得file id
        fileid = request.args['fileid']
        # TODO: 获得该文件的相关信息
        fileinfo = []
        # 返回文件信息
        return json.dumps(fileinfo), [('Content-Type', 'application/json;charset=utf-8')]
    elif 'directoryid' in request.args:
        # 获得directory id
        directoryid = request.args['directoryid']
        # TODO: 获得该目录的相关信息
        directoryinfo = []
        # 返回目录信息
        return json.dumps(directoryinfo), [('Content-Type', 'application/json;charset=utf-8')]


@app.route('/delete', methods=['POST'])
def delete():
    # TODO: 从数据库和文件系统中删除文件或目录及其相关信息
    status = ['success']
    return json.dumps(status), [('Content-Type', 'application/json;charset=utf-8')]


if __name__ == '__main__':
    app.run(port=8080)
