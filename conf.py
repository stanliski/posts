#-*- encoding: utf-8 -*-

import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = os.path.join(APP_DIR, 'blog.db')

PER_PAGE_NUM = 10