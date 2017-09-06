#!/usr/bin/env python3

import atexit
import json
import os
import re

import bs4

from . import api
from .config import session
from .logger import logger

HERE = os.path.dirname(os.path.realpath(__file__))
DATAFILE = os.path.join(HERE, 'photos.json')
MAPPING = {}

WEIBO_PHOTO_URL_PATTERN = re.compile(r'^http://photo.weibo.com/h5/')

def load():
    if os.path.isfile(DATAFILE):
        with open(DATAFILE) as fp:
            MAPPING.update(json.load(fp))

load()

def fetch(url):
    logger.info(f'resolving {url}')
    resp = session.get(url)
    assert resp.status_code == 200
    filename = os.path.basename(bs4.BeautifulSoup(resp.text, 'html.parser').find('img').get('src'))
    MAPPING[url] = filename
    api.ensure_sinaimg(filename)
    return filename

def resolve(url):
    return MAPPING[url] if url in MAPPING else fetch(url)

def persist():
    logger.info('persisting resolved photos')
    if not MAPPING:
        logger.warning('not persisting because there\'s no data to persist; '
                       'something might be wrong!')
        return
    with open(DATAFILE, 'w') as fp:
        json.dump(MAPPING, fp, indent=2, sort_keys=True)

atexit.register(persist)
