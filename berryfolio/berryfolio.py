# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
import shutil
from utils import *
from logger import logger
from dbOperation import DbConnect
from flask import Flask, render_template, g, make_response, json, request, session, redirect, url_for, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


# 我也不知道为什么，总之这句必须有
app = Flask(__name__)
generate_global(app.root_path)
app.config.from_object(__name__)  # load config from this file, berryfolio.py
# 加载默认配置
app.config.update(dict(
    SECRET_KEY='Thisismykeyafuibsvseibgf',
    UPLOADED_PHOTOS_DEST=config.GLOBAL['TEMP_PATH']
))

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB


def get_db():
    """在本次请求产生的全局变量g中创建一个唯一的数据库操作对象"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = DbConnect()
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
    logger.info('Initialized the database.')


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
@app.route('/home', methods=['GET'])
def home():
    if request.method == 'GET':
        if 'username' in session:
            username = session['username']
            # 检查到这个用户曾经登陆过
            db = get_db()
            if db.check_username(username):
                # 这是一个注册了的用户并且已经登录过，去个人主页
                return redirect(url_for('mypage'))
            else:
                # 未注册过的假冒用户，踢掉踢掉
                session.pop('username', None)
    return render_template('home.html')


# 用户登录页
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'GET':
        (verifycode, filename) = generate_verify_code()
        verifyurl = url_for('static', filename=filename)
        return render_template('login.html', message=message, varifyurl=verifyurl, verifycode=verifycode)
    elif request.method == 'POST':
        if request.form['type'] == 'Login':
            # 验证表单里的用户名密码
            username = request.form['username']
            password = request.form['password']
            code = request.form['verifycode']
            if code == request.form['code']:
                db = get_db()
                if db.match_user_pw(username, password):
                    # 登录成功，去mypage
                    session['username'] = username
                    return redirect(url_for('mypage'))
                else:
                    # 登录失败，滚回login
                    message = "登录失败，请重试"
            else:
                message = "验证码错误"
        elif request.form['type'] == 'Register':
            # 获得表单内容，检查并存入数据库，初始化目录并存入数据库
            # 未做SQL注入的防范
            username = request.form['username']
            password = request.form['password']
            code = request.form['verifycode']
            if code == request.form['code']:
                db = get_db()
                if db.add_user(username, password):
                    # 创建用户目录
                    make_user_dir(username)
                    # 在数据库中新增目录信息
                    if db.add_directory("root", 1, None, username):
                        # 创建用户目录下的根目录
                        make_user_sub_dir(username, None, "root")
                        # 注册成功，登录一下
                        message = "注册成功，请登录"
                    else:
                        logger.error("Fail to add dictionary: name=%s, user=%s" % ("root", username))
                        message = "注册失败，内部错误"
                else:
                    logger.error("Fail to register: username=%s" % username)
                    message = "注册失败，请重试"
            else:
                message = "验证码错误"
        logger.info("GET POST")
    return render_template('login.html', message=message)


# 个人主页，展示16张随机作品
@app.route('/mypage', methods=['GET', 'POST'])
def mypage(message):
    if 'username' in session:
        username = session['username']
        # 检查到这个用户曾经登陆过
        db = get_db()
        if db.check_username(username):
            # 这是一个注册了的用户，给你看自己的个人主页
            if request.method == 'GET':
                # 从数据库获取这个用户的个人作品，传入模板
                filelist = db.get_files_by_user(username)
                entity = None
                if filelist:
                    length = len(filelist)
                    if 16 > length > 0:
                        # 填充至16
                        filelist = (filelist * (16 / length + 1))[:16]
                    # 选16并构造url
                    entity = map(lambda fid: [url_for('static', filename=db.get_file_path(fid))],
                                 random.sample(filelist, 16))
                else:
                    message = "获取作品信息失败"
                return render_template('mypage.html', entity=entity, username=username, message=message)
            elif request.method == 'POST':
                # TODO: 获得表单内容，检查并存入数据库，更新用户设置
                message = "用户设置已更新"
                return redirect(url_for(mypage, message=message))
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


# 个人管理页面
@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio(message):
    if 'username' in session:
        username = session['username']
        # 检查到这个用户曾经登陆过
        db = get_db()
        if db.check_username(username):
            # 这是一个注册了的用户，给你管理自己的作品集
            if request.method == 'GET':
                # 从数据库获取这个用户的目录信息，传入模板
                root_id = db.get_dir_root(username)
                try:
                    tree = db.generate_tree(root_id)
                except Exception as ex:
                    logger.error("Failure in constructing directory tree: " + ex.message)
                    message = "获取目录信息失败"
                    tree = {}
                return render_template('portfolio.html', tree=tree, username=username, message=message)
            elif request.method == 'POST':
                message = "未知上传类型"
                if request.form['type'] == 'Photo' and 'photo' in request.files:
                    # 获取表单内容
                    pid = request.form['parentID']
                    input_name = request.form['filename']
                    description = request.form['description']
                    dir_name = db.get_name(pid, 1)
                    dir_path = os.path.join(config.GLOBAL['DATA_PATH'], username,
                                            db.gen_parent_path(dir_id=pid), dir_name)
                    # 保存文件至临时目录
                    filename = photos.save(request.files['photo'])
                    file_path_old = os.path.join(config.GLOBAL['TEMP_PATH'], filename)
                    file_path = os.path.join(dir_path, filename)
                    # 文件信息存入数据库
                    fid = db.add_file(pid, input_name, description, file_path, username)
                    if fid:
                        # 为文件添加数字水印
                        if add_watermark(add_data_path_prefix(file_path_old),
                                         add_data_path_prefix(file_path), config.GLOBAL['WM_PATH']):
                            message = "上传成功"
                        else:
                            # TODO: 添加水印失败，回滚数据库操作
                            # db.del_file(fileID)
                            message = "内部错误"
                    else:
                        message = "上传失败"
                elif request.form['type'] == 'Attribute':
                    # 获取表单内容
                    fid = request.form['fileID']
                    pid = request.form['parentID']
                    filename = request.form['filename']
                    description = request.form['description']
                    file_path_old = db.get_file_path(fid)
                    file_path = os.path.join(username, db.gen_parent_path(dir_id=pid),
                                             file_path_old.split('\\')[-1])
                    # 存入数据库
                    if db.update_file_info(fid, pid, filename, description, file_path):
                        # 比对文件位置
                        if file_path != file_path_old:
                            # 移动文件
                            shutil.move(add_data_path_prefix(file_path_old),
                                        add_data_path_prefix(file_path))
                        message = "修改成功"
                    else:
                        message = "修改失败"
                elif request.form['type'] == 'Directory':
                    # 获取表单内容
                    dname = request.form['name']
                    dtype = request.form['type']
                    pid = request.form['parentID']
                    # 存入数据库
                    did = db.add_directory(dname, dtype, pid, username)
                    if did:
                        # 新增目录
                        parentpath = db.gen_parent_path(dir_id=pid)
                        make_user_sub_dir(username, parentpath, dname)
                        message = "增加目录成功"
                    else:
                        message = "增加目录失败"
                redirect(url_for(portfolio, message=message))
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


# 下载接口
@app.route('/download', methods=['GET'])
def download():
    if 'username' in session:
        username = session['username']
        # 检查到这个用户曾经登陆过
        db = get_db()
        if db.check_username(username):
            # 这是一个注册了的用户，给你下载
            if 'fileid' in request.args:
                # 获得file id
                fileid = request.args['fileid']
                # 构造指向该文件的下载链接
                filepath = os.path.join('data', db.get_file_path(fileid))
                return app.send_static_file(filepath)
            elif 'directoryid' in request.args:
                # 获得directory id
                directoryid = request.args['directoryid']
                # 构造目录路径
                directory_name = db.get_name(directoryid, 1)
                parentpath = db.gen_parent_path(dir_id=directoryid)
                directory_path = add_data_path_prefix(os.path.join(username, parentpath, directory_name))
                # 生成压缩包
                zip_name = username + ".zip"
                zip_path = make_zip(directory_path, zip_name)
                if zip_path:
                    # 构造指向该压缩包的下载链接
                    return send_from_directory(config.GLOBAL['TEMP_PATH'], zip_name, as_attachment=True)
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


# 查询接口
@app.route('/query', methods=['GET'])
def query():
    if 'fileid' in request.args:
        # 获得file id
        fileid = request.args['fileid']
        db = get_db()
        # 获得该文件的相关信息
        fileinfo = db.get_file_info(fileid)
        # fileinfo['status']代表获取状态
        # if fileinfo is None:
        #     fileinfo = {"status": "Failed"}
        # 返回文件信息
        return json.dumps(fileinfo), [('Content-Type', 'application/json;charset=utf-8')]


# 删除接口
@app.route('/delete', methods=['POST'])
def delete():
    # TODO: 从数据库和文件系统中删除文件或目录及其相关信息
    status = ['success']
    return json.dumps(status), [('Content-Type', 'application/json;charset=utf-8')]


if __name__ == '__main__':
    app.run(port=8080)
