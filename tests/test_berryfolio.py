# -*- coding: utf-8 -*-
import os
import berryfolio
import unittest
import tempfile


class BerryfolioTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, berryfolio.app.config['TEST_DATABASE'] = tempfile.mkstemp()
        self.db_fd, berryfolio.GLOBAL['DB_PATH'] = tempfile.mkstemp()
        berryfolio.app.testing = True
        self.app = berryfolio.app.test_client()
        with berryfolio.app.app_context():
            berryfolio.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(berryfolio.GLOBAL['DB_PATH'])

    def test_homepage(self):
        rv = self.app.get('/')
        assert "<h1>Hello</h1>" in rv.data

    def register(self, username, password, vcode):
        return self.app.post('/register', data=dict(
            btn=u"Register",
            username=username,
            password=password,
            vcode=vcode,
            code=u"1234"
        ), follow_redirects=True)

    def login(self, username, password, vcode):
        return self.app.post('/login', data=dict(
            btn=u"Login",
            username=username,
            password=password,
            vcode=vcode,
            code=u"1234"
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def mypage(self):
        return self.app.get('/mypage', follow_redirects=True)

    def test_register_login_logout(self):
        # 注册
        rv = self.register(u'admin', u'default', u'1234')
        assert "用户登录" in rv.data
        rv = self.register(u'2', u'2', u'1111')
        assert "验证码错误" in rv.data
        rv = self.register(u'admin', u'default', u'1234')
        assert "注册失败，请重试" in rv.data
        # 登录
        rv = self.login(u'admin', u'defaultx', u'1234')
        assert "登录失败，请重试" in rv.data
        rv = self.login(u'admin', u'default', u'1111')
        assert "验证码错误" in rv.data
        rv = self.login(u'admin', u'default', u'1234')
        print rv.data
        assert "欢迎进入Berryfolio" in rv.data
        # 登出
        rv = self.logout()
        assert '欢迎使用Berryfolio' in rv.data

    def test_mypage(self):
        # 登录
        rv = self.login(u'Yunzhe', u'123', u'1234')
        assert "欢迎进入Berryfolio" in rv.data
        # 转到个人页面
        rv = self.mypage()
        assert "欢迎进入Berryfolio" in rv.data
        # 登出
        rv = self.logout()
        assert '欢迎使用Berryfolio' in rv.data
        # 尝试打开个人页面
        rv = self.mypage()
        assert '欢迎使用Berryfolio' in rv.data

    def upload(self):
        pass

    def modify(self):
        pass

    def directory(self):
        pass

    def test_upload_modify_directory(self):
        pass

    def download(self):
        pass

    def test_download(self):
        pass


if __name__ == '__main__':
    unittest.main()
