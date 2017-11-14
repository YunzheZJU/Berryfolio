# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import os
import time
import shutil
import hashlib
from utils import *
from logger import logger
from dbOperation import DbConnect
from flask import Flask, render_template, g, make_response, json, request, session, redirect, url_for, \
    send_from_directory, abort
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
    # 假装注册了几个新用户
    # 第一个
    uid_1 = db.add_user(u"Yunzhe", u"123", 'images/avatar.jpg', u'这个人很懒', u'我的作品集', u'这是我的作品集')
    make_user_dir(uid_1)
    did_1_1 = db.add_directory(u"root", 1, None, uid_1)
    make_user_sub_dir(uid_1, None, did_1_1)
    # 第二个
    uid_2 = db.add_user(u"一个用户", u"password", 'images/avatar.jpg', u'sdgdg', u'egweag', u'ewgere')
    make_user_dir(uid_2)
    did_2_1 = db.add_directory(u"新文件夹", 1, None, uid_2)
    make_user_sub_dir(uid_2, None, did_2_1)
    # 假装新建了很多文件夹
    did_1_2 = db.add_directory(u"sub1", 2, did_1_1, uid_1)
    make_user_sub_dir(uid_1, str(did_1_1), did_1_2)
    did_1_3 = db.add_directory(u"sub2", 1, did_1_1, uid_1)
    make_user_sub_dir(uid_1, str(did_1_1), did_1_3)
    did_1_4 = db.add_directory(u"sub3", 1, did_1_1, uid_1)
    make_user_sub_dir(uid_1, str(did_1_1), did_1_4)
    did_1_5 = db.add_directory(u"folder1", 1, did_1_3, uid_1)
    make_user_sub_dir(uid_1, db.gen_parent_path(did_1_3), did_1_5)
    did_1_6 = db.add_directory(u"folder2", 2, did_1_5, uid_1)
    make_user_sub_dir(uid_1, db.gen_parent_path(did_1_5), did_1_6)
    # 上传一些文件
    # 第一个
    file_path_old = os.path.join(config.GLOBAL['TEMP_PATH'], "source.jpg")
    file_path = add_data_path_prefix(os.path.join(str(uid_1), db.gen_parent_path(did_1_2), "source1.png"))
    (fm, w, h) = add_watermark(add_data_path_prefix(file_path_old),
                               add_data_path_prefix(file_path), config.GLOBAL['WM_PATH'])
    fid_1_1 = db.add_file(did_1_2, u"我的照片1", u"对它的描述1", file_path, uid_1, fm, w, h, u"标签1", u"标2", u"3")
    # 第二个
    file_path_old = os.path.join(config.GLOBAL['TEMP_PATH'], "source.jpg")
    file_path = add_data_path_prefix(os.path.join(str(uid_1), db.gen_parent_path(did_1_2), "source2.png"))
    (fm, w, h) = add_watermark(add_data_path_prefix(file_path_old),
                               add_data_path_prefix(file_path), config.GLOBAL['WM_PATH'])
    fid_1_2 = db.add_file(did_1_2, u"我的照片2", u"对它的描述2", file_path, uid_1, fm, w, h, u"标1", u"标", u"4")


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
    if 'uid' in session:
        uid = int(session['uid'])
        # 检查到这个用户曾经登陆过
        db = get_db()
        username = db.get_name(uid, 0)
        if username:
            # 这是一个注册了的用户并且已经登录过，去个人主页
            return redirect(url_for('mypage'))
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('uid', None)
    return render_template('index_logout.html')


# 用户注册页
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    (vcode, filename) = generate_verify_code()
    # vcode_url = url_for('static', filename=filename).decode('utf-8')
    if request.method == 'POST':
        # 获得表单内容，检查并存入数据库，初始化目录并存入数据库（未做SQL注入的防范）
        username = request.form['username']
        password = request.form['password']
        code = request.form['vcode']
        if code == request.form['code']:
            db = get_db()
            uid = db.add_user(username, password, 'images/avatar.jpg', u'这个人很懒', u'我的作品集', u'这是我的作品集')
            if uid:
                # 创建用户目录
                if make_user_dir(uid):
                    # 在数据库中新增目录信息
                    did = db.add_directory(u"root", 1, None, uid)
                    if did:
                        # 创建用户目录下的根目录
                        make_user_sub_dir(uid, None, did)
                        # 注册成功，登录一下
                        return redirect(url_for('login'))
                    else:
                        logger.error("Fail to add dictionary: name=%s, user=%s" % ("root", username))
                        message = u"注册失败，内部错误"
                else:
                    message = u"注册失败，读写错误"
            else:
                logger.error("Fail to register: username=%s" % username)
                message = u"注册失败，请重试"
        else:
            message = u"验证码错误"
    return render_template('register.html', message=message, vcode=vcode)


# 用户登录页
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    (vcode, filename) = generate_verify_code()
    # vcode_url = url_for('static', filename=filename).decode('utf-8')
    if request.method == 'POST':
        # 验证表单里的用户名密码
        username = request.form['username']
        password = request.form['password']
        code = request.form['vcode']
        if code == request.form['code']:
            db = get_db()
            uid = db.match_user_pw(username, password)
            if uid:
                # 登录成功，去mypage
                session['uid'] = uid
                return redirect(url_for('mypage'))
            else:
                # 登录失败，滚回login
                message = u"登录失败，请重试"
        else:
            message = u"验证码错误"
    return render_template('login.html', message=message, vcode=vcode)


# 用户登出
@app.route('/logout', methods=['GET'])
def logout():
    if 'uid' in session:
        session.pop('uid', None)
    return redirect(url_for('home'))


# 条款
@app.route('/contract', methods=['GET'])
def contract():
    return render_template('contract.html')


# 个人主页，展示16张随机作品
@app.route('/mypage', methods=['GET'])
def mypage():
    message = None
    if 'uid' in session:
        uid = int(session['uid'])
        # 检查到这个用户曾经登陆过
        db = get_db()
        username = db.get_name(uid, 0)
        if username:
            # 这是一个注册了的用户，给你看自己的个人主页
            # 从数据库获取这个用户的个人作品，传入模板
            file_list = db.get_files_by_user(uid)
            entity = []
            if file_list is not None:
                # 获取成功
                length = len(file_list)
                if length > 0:
                    if length < 16:
                        # 填充至16
                        file_list = (file_list * (16 / length + 1))[:16]
                    # 选16并构造url
                    for fid in random.sample(file_list, 16):
                        file_info = db.get_file_info(fid)
                        entity.append(get_file_info(file_info))
                else:
                    # length == 0
                    # 填充缺省图像
                    entity = [get_file_info({'status': 'failed'})] * 16
            else:
                # 获取失败
                message = u"获取作品信息失败"
            return render_template('index_login.html', entity_0=entity[0:4], entity_1=entity[4:6],
                                   entity_2=entity[6:16], username=username, message=message,
                                   avatar_url=url_for('static', filename=db.get_avatar(uid)))
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('uid', None)
    return redirect(url_for('home'))


# 设置页面
@app.route('/setting', methods=['GET', 'POST'])
def setting():
    message = None
    if 'uid' in session:
        uid = int(session['uid'])
        # 检查到这个用户曾经登陆过
        db = get_db()
        username = db.get_name(uid, 0)
        if username:
            # 这是一个注册了的用户，允许你更改设置
            results = db.get_user_info(uid)
            if request.method == 'POST':
                # 获得上传的文件和信息，改变头像大小并保存，数据入库
                # 获取表单内容
                introduction = request.form['introduction']
                input_name = request.form['name']
                description = request.form['description']
                file_path = results[0]
                if 'avatar' in request.files and request.files['avatar']:
                    # 保存文件至临时目录
                    m = hashlib.md5()
                    m.update(str(time.time()))
                    filename = photos.save(request.files['avatar'], name=m.hexdigest() + ".")
                    file_path = "images/avatar" + "/" + filename
                    # 设置头像尺寸并保存
                    resize_avatar(filename, file_path)
                # 文件信息存入数据库
                if db.update_user_info(uid, file_path, introduction, input_name, description):
                    message = u"更新设置成功"
                    results = db.get_user_info(uid)
                else:
                    message = u"更新设置失败"
            return render_template('setting.html', message=message, username=username,
                                   avatar=url_for('static', filename=results[0]), introduction=results[1],
                                   name=results[2], description=results[3])
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


# 个人管理页面
@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    message = None
    if 'uid' in session:
        uid = int(session['uid'])
        # 检查到这个用户曾经登陆过
        db = get_db()
        username = db.get_name(uid, 0)
        if username:
            # 这是一个注册了的用户，给你管理自己的作品集
            # if request.method == 'GET':
                # # 从数据库获取这个用户的目录信息，传入模板
                # root_id = db.get_dir_root(uid)
                # try:
                #     tree = db.generate_tree(root_id)
                # except Exception as ex:
                #     logger.error("Failure in constructing directory tree: " + ex.message)
                #     message = u"获取目录信息失败"
                #     tree = {}
                # return render_template('portfolio.html', username=username, message=message)
            if request.method == 'POST':
                message = u"未知上传类型"
                if request.form['type'] == u'Photo' and 'photo' in request.files:
                    # 获取表单内容
                    pid = int(request.form['pid'])
                    input_name = request.form['title']
                    description = request.form['description']
                    tag_1 = request.form['tag_1']
                    tag_2 = request.form['tag_2']
                    tag_3 = request.form['tag_3']
                    dir_path = add_data_path_prefix(os.path.join(str(uid), db.gen_parent_path(pid)))
                    # 保存文件至临时目录
                    m = hashlib.md5()
                    m.update(str(time.time()))
                    filename = photos.save(request.files['photo'], name=m.hexdigest() + ".")
                    file_path_old = os.path.join(config.GLOBAL['TEMP_PATH'], filename)
                    ext = filename.split(".")[-1]
                    filename = filename.replace(ext, "png")
                    file_path = os.path.join(dir_path, filename)
                    # 为文件添加数字水印
                    (fm, width, height) = add_watermark(add_data_path_prefix(file_path_old),
                                                        add_data_path_prefix(file_path), config.GLOBAL['WM_PATH'])
                    if fm:
                        # 文件信息存入数据库
                        fid = db.add_file(pid, input_name, description, file_path, uid, fm, width, height,
                                          tag_1, tag_2, tag_3)
                        if fid:
                            message = u"上传成功"
                        else:
                            message = u"上传失败"
                    else:
                        message = u"读取错误"
                elif request.form['type'] == u'Attribute':
                    # 获取表单内容
                    fid = int(request.form['fid'])
                    pid = int(request.form['pid'])
                    title = request.form['title']
                    tag_1 = request.form['tag_1']
                    tag_2 = request.form['tag_2']
                    tag_3 = request.form['tag_3']
                    description = request.form['description']
                    file_path_old = db.get_file_path(fid)
                    file_path = add_data_path_prefix(os.path.join(str(uid), db.gen_parent_path(pid),
                                                                  file_path_old.split('\\')[-1]))
                    # 存入数据库
                    if db.update_file_info(fid, pid, title, description, file_path, tag_1, tag_2, tag_3):
                        # 比对文件位置
                        if file_path != file_path_old:
                            # 移动文件
                            shutil.move(add_data_path_prefix(file_path_old),
                                        add_data_path_prefix(file_path))
                        message = u"修改成功"
                    else:
                        message = u"修改失败"
                elif request.form['type'] == u'Directory':
                    # 获取表单内容
                    name = request.form['name']
                    rtype = 1 if request.form['rtype'] == u"on" else 2
                    pid = int(request.form['pid'])
                    # 存入数据库
                    did = db.add_directory(name, rtype, pid, uid)
                    if did:
                        # 新增目录
                        parent_path = db.gen_parent_path(pid)
                        make_user_sub_dir(uid, parent_path, did)
                        message = u"增加目录成功"
                    else:
                        message = u"增加目录失败"
            return render_template('portfolio.html', uid=uid, username=username, introduction=db.get_user_info(uid)[1],
                                   message=message, root_id=db.get_dir_root(uid))
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/search', methods=['POST'])
def search():
    # message = None
    if 'uid' in session:
        uid = int(session['uid'])
        # 检查到这个用户曾经登陆过
        db = get_db()
        username = db.get_name(uid, 0)
        if username:
            # 这是一个注册了的用户，给你搜索
            keyword = request.form['keyword']
            results = db.search_files(keyword)
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


# 下载接口
@app.route('/download', methods=['GET'])
def download():
    # message = None
    if 'uid' in session:
        uid = int(session['uid'])
        # 检查到这个用户曾经登陆过
        db = get_db()
        username = db.get_name(uid, 0)
        if username:
            # 这是一个注册了的用户，给你下载
            if 'fid' in request.args:
                # 获得file id
                fid = int(request.args['fid'])
                # 构造指向该文件的下载链接
                file_path = remove_data_path_prefix(db.get_file_path(fid))
                return redirect(url_for('data', filename=file_path, _external=True))
            elif 'did' in request.args:
                # 获得directory id
                did = int(request.args['did'])
                # 构造目录路径
                directory_path = add_data_path_prefix(os.path.join(str(uid), db.gen_parent_path(did)))
                # 生成压缩包
                zip_name = make_zip(db, directory_path, username)
                print zip_name
                if zip_name:
                    # 构造指向该压缩包的下载链接
                    return send_from_directory(config.GLOBAL['TEMP_PATH'], zip_name, as_attachment=True)
        else:
            # 未注册过的假冒用户，踢掉踢掉
            session.pop('username', None)
    return redirect(url_for('home'))


# 查询接口
@app.route('/query', methods=['GET'])
def query():
    """
    查询接口
    :return: 请求fid时，返回文件信息，形如
        {"description": "\u5bf9\u5b83\u7684\u63cf\u8ff01", "filename": "\u6211\u7684\u7167\u72471", "status": "success"}
        >   $.get("query", {'fid':1}, function(data){console.log(data)})
            {description: "对它的描述1", status: "success", title: "我的照片1"}
    :return: 请求uid和type时，返回该用户的类型为type的文件夹(id: name)，形如
        >   $.get("query", {'uid':1, 'type':1}, function(data){console.log(data)})
            {1: "root", 4: "sub2", 5: "sub3", 6: "folder1"}
        >   $.get("query", {'uid':1, 'type':2}, function(data){console.log(data)})
            {3: "sub1"}
    :return: 请求did时，返回该目录下子目录或文件的id组成的list和名字组成的list，
        'type'键存储该父目录的类型，同时也表示子元素的类型，形如
        >   $.get("query", {'did':1}, function(data){console.log(data)})
            {list: [3, 4, 5], type: 1}
            可以这样获取值：data['list'][1]（值为4）
        >   $.get("query", {'did':3}, function(data){console.log(data)})
            {list: [1, 2], type: 2}
    """
    if 'fid' in request.args:
        # 获得file id
        fid = int(request.args['fid'])
        db = get_db()
        # 获得该文件的相关信息
        file_info = db.get_file_info(fid)
        if file_info['status'] == 'success':
            file_info['path'] = remove_root_path_prefix(file_info['path'])
        # 返回文件信息
        return json.dumps(file_info), [('Content-Type', 'application/json;charset=utf-8')]
    if 'uid' in request.args and 'type' in request.args:
        uid = int(request.args['uid'])
        rtype = int(request.args['type'])
        db = get_db()
        did_list = db.get_dirs_by_user(uid, rtype)
        result = {}
        for did in did_list:
            result[did] = db.get_name(did, 1)
        return json.dumps(result), [('Content-Type', 'application/json;charset=utf-8')]
    if 'did' in request.args:
        did = int(request.args['did'])
        db = get_db()
        children = db.get_dir_children(did)
        if children:
            d_type = children[0]
            children = children[1:]
            result = {'type': [], 'List': children, 'dName': []}
            for cid in children:
                result['dName'].append(db.get_name(cid, d_type))
                result['type'].append(db.get_dir_type(cid))
        else:
            result = {}
        return json.dumps(result), [('Content-Type', 'application/json;charset=utf-8')]


# 删除接口
@app.route('/delete', methods=['POST'])
def delete():
    # TODO: 从数据库和文件系统中删除文件或目录及其相关信息
    if 'fid' in request.args:
        # 删除文件
        pass
    elif 'did' in request.args:
        pass
    status = ['success']
    return json.dumps(status), [('Content-Type', 'application/json;charset=utf-8')]


# /data路由
@app.route('/data/<path:filename>', methods=['GET'])
def data(filename):
    return send_from_directory(config.GLOBAL['DATA_PATH'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(port=8080)
