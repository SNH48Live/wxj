#!/usr/bin/env python3

import atexit
import json
import os
import re

from .config import session
from .logger import logger

HERE = os.path.dirname(os.path.realpath(__file__))
DATAFILE = os.path.join(HERE, 'emojis.json')
ROOT = os.path.dirname(HERE)
EMOJISDIR = os.path.join(ROOT, 'images', 'emojis')

EMOJIS = {
    'apple': {},
    'pictorial': {},
}

def load():
    if os.path.isfile(DATAFILE):
        with open(DATAFILE) as fp:
            EMOJIS.update(json.load(fp))

load()

def emoji(label):
    if label in EMOJIS['apple']:
        return EMOJIS['apple'][label]
    elif label in EMOJIS['pictorial']:
        filename = EMOJIS['pictorial'][label]
        path = f'/assets/images/emojis/{filename}'
        return f'<img src="{path}" alt="[{label}]">'
    else:
        return f'[{label}]'

def save_mweibocn_emoji(label, classes):
    assert classes[0] == 'face'
    assert classes[1].startswith('face_')
    i = int(classes[1][5:])
    assert classes[2].startswith('icon_')
    j = int(classes[2][5:])
    filename = f'm.weibo.cn-{i}-{j}.png'
    if label in EMOJIS['pictorial']:
        assert EMOJIS['pictorial'][label] == filename
    else:
        EMOJIS['pictorial'][label] = filename

EMOJI_PLACEHOLDER = re.compile(r'\[(?P<label>[^\]]+)\]')

def markup_emojis(text):
    return EMOJI_PLACEHOLDER.sub(lambda m: emoji(m.group('label')), text)

# Some of the emojis in statuses returned by m.weibo.cn API are direct
# image links to h5.sinaimg.cn/m/emoticon/icon/..., which we should
# resolve into local emojis.
SINAIMG_EMOJI_URL = re.compile(r'^https?://h5\.sinaimg\.cn/m/emoticon/.*/(?P<name>\w+)-[0-9a-f]+\.png$')
def resolve_linked_emoji(url):
    if url.startswith('//'):
        url = f'http:{url}'
    m = SINAIMG_EMOJI_URL.match(url)
    filename = (m.group('name') + '.png') if m else os.path.basename(SINAIMG_EMOJI_URL)
    localpath = os.path.join(EMOJISDIR, filename)

    if not os.path.exists(localpath):
        logger.info(f'downloading {url}')
        try:
            resp = session.get(url, stream=True)
            assert resp.status_code == 200
            with open(localpath, 'wb') as fp:
                for chunk in resp.iter_content(16384):
                    fp.write(chunk)
        except Exception:
            logger.error(f'failed to download {url}')

    return f'/assets/images/emojis/{filename}'

def persist():
    logger.info('persisting emoji mapping')
    if not EMOJIS:
        logger.warning('not persisting because there\'s no data to persist; '
                       'something might be wrong!')
        return
    with open(DATAFILE, 'w') as fp:
        json.dump(EMOJIS, fp, indent=2, ensure_ascii=False, sort_keys=True)

atexit.register(persist)
