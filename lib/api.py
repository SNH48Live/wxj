#!/usr/bin/env python3

import http
import json
import os
import random
import re
import subprocess

from . import config, db
from .logger import logger

UID = config.uid

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(HERE)
APIDIR = os.path.join(ROOT, 'api')
APIDIR_COMPLETE = os.path.join(APIDIR, 'complete')
IMAGEDIR = os.path.join(ROOT, 'images')
THUMBNAILER = os.path.join(ROOT, 'bin', 'thumbnail')

os.makedirs(APIDIR_COMPLETE, exist_ok=True)
os.makedirs(os.path.join(IMAGEDIR, 'large'), exist_ok=True)
os.makedirs(os.path.join(IMAGEDIR, 'thumb180'), exist_ok=True)

def ensure_sinaimg(basename):
    for res in ['large', 'thumb180']:
        rand = random.randrange(1, 5)
        url = f'http://ww{rand}.sinaimg.cn/{res}/{basename}'
        localpath = os.path.join(IMAGEDIR, res, basename)
        if os.path.exists(localpath):
            continue
        logger.info(f'downloading {url}')
        try:
            resp = session.get(url, stream=True)
            assert resp.status_code == 200
            with open(localpath, 'wb') as fp:
                for chunk in resp.iter_content(16384):
                    fp.write(chunk)
        except Exception:
            logger.error(f'failed to download {url}')

    for res in ['thumb120', 'thumb240', 'thumb360']:
        localpath = os.path.join(IMAGEDIR, res, basename)
        if not os.path.exists(localpath):
            break
    else:
        # All thumbnails have already been generated
        return
    # Generate thumbnails
    logger.info(f'generating thumbnails for {basename}')
    subprocess.run([THUMBNAILER, basename])

def load_status(sid):
    filesystem_path = os.path.join(APIDIR, f'{sid}.json')
    with open(filesystem_path) as fp:
        return json.load(fp)

STATUS_JSON_FILE = re.compile(r'^(?P<sid>\d+)\.json$')

def list_existing_sids():
    sids = []
    for filename in os.listdir(APIDIR):
        m = STATUS_JSON_FILE.match(filename)
        if m:
            sids.append(m.group('sid'))
    return sids

def fetch_and_save_complete_status(sid):
    logger.info(f'fetching status {sid}')
    resp = session.get(
        f'http://m.weibo.cn/statuses/extend?id={sid}',
        headers={'Referer': f'http://m.weibo.com/status/{sid}'},
    )
    assert resp.status_code == 200
    obj = resp.json()
    assert obj['ok'] == 1

    filesystem_path = os.path.join(APIDIR_COMPLETE, f'{sid}.json')
    with open(filesystem_path, 'w') as fp:
        json.dump(obj, fp, ensure_ascii=False, sort_keys=True, indent=2)

    return obj['longTextContent']

def load_complete_status(sid):
    filesystem_path = os.path.join(APIDIR_COMPLETE, f'{sid}.json')
    with open(filesystem_path) as fp:
        return json.load(fp)['longTextContent']

def resolve_complete_status(sid):
    try:
        return load_complete_status(sid)
    except Exception:
        return fetch_and_save_complete_status(sid)
