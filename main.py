# -*- coding: utf-8 -*-
# 为方便阅读，使用中文注释
import dbOperation
from flask import Flask, url_for, render_template, request

# 我也不知道为什么，总之这句必须有
app = Flask(__name__)


# 这是通往网站首页的大门
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html'), 200, {'Cache-Control': 'no-cache'}
