#!/usr/bin/env python3

import os
import urllib.parse

import yaml

from .logger import logger

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(HERE)

site_root = None
builddir = None
local_images = None
statuses_per_page = None

def load(config_file=None):
    if config_file is None:
        config_file = os.path.join(ROOT, 'conf.yml')
    logger.debug(f'loading configurations from {config_file}')
    with open(config_file) as fp:
        config = yaml.load(fp.read())

    global site_root
    global builddir
    global local_images
    global statuses_per_page
    site_root = config.get('site_root', '/')
    builddir = config.get('builddir', 'public')
    if not os.path.isabs(builddir):
        builddir = os.path.join(ROOT, builddir)
    local_images = config.get('local_images', True)
    statuses_per_page = config.get('statuses_per_page', 20)

def site_path(path):
    if path.startswith('/'):
        path = path[1:]
    return urllib.parse.urljoin(site_root, path)

def asset_path(path):
    if path.startswith('/'):
        path = path[1:]
    return site_path(urllib.parse.urljoin('/assets/', path))

if 'CONFIG_FILE' in os.environ:
    config_file = os.getenv('CONFIG_FILE')
    if not os.path.isabs(config_file):
        config_file = os.path.join(ROOT, config_file)
    load(config_file)
else:
    load()
