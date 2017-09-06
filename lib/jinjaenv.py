#!/usr/bin/env python3

import os
from contextlib import contextmanager

import arrow
import jinja2

from . import config, emojis, utils, version

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE_DIR = os.path.join(ROOT, 'templates')
JINJAENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
)

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

GLOBALS = JINJAENV.globals
GLOBALS['CSS_VERSION'] = version.css_version
GLOBALS['JS_VERSION'] = version.js_version
GLOBALS['LOCAL_IMAGES'] = config.local_images

FILTERS = JINJAENV.filters
FILTERS['localimgpath'] = utils.localimgpath
FILTERS['markup'] = markup
FILTERS['sinaimgpath'] = utils.sinaimgpath
FILTERS['strftime'] = strftime
