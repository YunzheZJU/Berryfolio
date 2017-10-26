# -*- coding: utf-8 -*-
import os
import berryfolio
import unittest
import tempfile


class BerryfolioTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, berryfolio.app.config['DATABASE'] = tempfile.mkstemp()
        berryfolio.app.testing = True
        self.app = berryfolio.app.test_client()
        with berryfolio.app.app_context():
            berryfolio.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(berryfolio.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'text/javascript' in rv.data


if __name__ == '__main__':
    unittest.main()
