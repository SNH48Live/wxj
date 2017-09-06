#!/usr/bin/env python3

import http.cookies
import os

import requests
import yaml

from .logger import logger

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(HERE)

builddir = None
local_images = None
statuses_per_page = None
uid = None
session = requests.Session()

def load_cookies(s):
    cookies = http.cookies.SimpleCookie()
    cookies.load(s)
    for key, morsel in cookies.items():
        session.cookies.set(key, morsel.value, domain='weibo.com')

def load(config_file=None):
    if config_file is None:
        config_file = os.path.join(ROOT, 'conf.yml')
    logger.debug(f'loading configurations from {config_file}')
    with open(config_file) as fp:
        config = yaml.load(fp.read())

    global builddir
    global local_images
    global statuses_per_page
    global uid
    builddir = config.get('builddir', '_build')
    if not os.path.isabs(builddir):
        builddir = os.path.join(ROOT, builddir)
    local_images = config.get('local_images', True)
    statuses_per_page = config.get('statuses_per_page', 20)
    uid = config.get('uid', 3053424305)

    cookies = config.get('cookies', '')
    user_agent = config.get('user_agent', 'Safari')
    load_cookies(cookies)
    session.headers['User-Agent'] = user_agent

if 'MOMOCONF' in os.environ:
    config_file = os.getenv('MONOCONF')
    if not os.path.isabs(config_file):
        config_file = os.path.join(ROOT, config_file)
    load(config_file)
else:
    load()
