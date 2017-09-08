#!/usr/bin/env python3

import os
from contextlib import contextmanager

import arrow
import jinja2

from . import config, emojis, utils
from .common import TEMPLATESDIR

JINJAENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.fspath(TEMPLATESDIR)),
)
GLOBALS = JINJAENV.globals
FILTERS = JINJAENV.filters

def init():
    GLOBALS['LOCAL_IMAGES'] = config.values.local_images

@contextmanager
def setglobal(name, value):
    has_original_value = False
    original_value = None
    if name in GLOBALS:
        has_original_value = True
        original_value = GLOBALS[name]

    GLOBALS[name] = value
    yield

    if has_original_value:
        GLOBALS[name] = original_value
    else:
        del GLOBALS[name]

def markup(text):
    text = emojis.markup_emojis(text)
    return text

def strftime(timestamp):
    return arrow.get(timestamp).to('Asia/Shanghai').strftime('%Y-%m-%d %H:%M:%S')

FILTERS['assetpath'] = utils.asset_path
FILTERS['localimgpath'] = utils.local_image_path
FILTERS['markup'] = markup
FILTERS['sinaimgpath'] = utils.sina_image_path
FILTERS['sitepath'] = utils.site_path
FILTERS['strftime'] = strftime
