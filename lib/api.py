#!/usr/bin/env python3

import http
import json
import os
import random
import re
import subprocess

from . import config, db
from .config import session
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

def fetch_statuses(page=1):
    logger.info(f'fetching page {page}')
    resp = session.get(
        f'http://m.weibo.cn/container/getIndex?type=uid&value={UID}&containerid=107603{UID}&page={page}',
        headers={'Referer': f'http://m.weibo.com/u/{UID}'},
    )
    assert resp.status_code == 200
    return resp.json()['cards']

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

MWEIBOCN_STATUS_LINK = re.compile(r'^https?://m\.weibo\.cn/status/(?P<basename>\w+)(\?.*)?')

# Returns the transformed JSON object, and a bool indicating when the
# status is new (hasn't been saved to disk before).
def save_status(json_):
    if 'mblog' in json_:
        # Fetch images
        if 'pics' in json_['mblog']:
            for pic in json_['mblog']['pics']:
                ensure_sinaimg(os.path.basename(pic['url']))
        if 'retweeted_status' in json_['mblog']:
            if 'pics' in json_['mblog']['retweeted_status']:
                for pic in json_['mblog']['retweeted_status']['pics']:
                    ensure_sinaimg(os.path.basename(pic['url']))

        sid = json_['mblog']['id']
        filesystem_path = os.path.join(APIDIR, f'{sid}.json')
        if os.path.exists(filesystem_path):
            return json_, False

        # Inject the timestamp into the JSON object, as
        # .mblog._created_at. This timestamp has a second-level
        # granularity compared to that of .mblog.created_at, which only
        # has minute-level granularity. Also, .mblog.created_at is a
        # printable datetime (which could be a relative time) not that
        # fun to parse.
        timestamp = fetch_timestamp(sid, MWEIBOCN_STATUS_LINK.match(json_['scheme']).group('basename'))
        json_['mblog']['_created_at'] = timestamp

        with open(filesystem_path, 'w') as fp:
            json.dump(json_, fp, ensure_ascii=False, sort_keys=True, indent=2)

        return json_, True
    else:
        return None, False

# pages == 0 means fetch all pages (stop when a page is empty)
# If update is True, stop when a saved status is encountered
def fetch_and_save(pages=0, start=1, update=True):
    page = start
    while page <= pages or pages == 0:
        cards = fetch_statuses(page)

        if not cards:
            # Reached the end of all statuses
            logger.warning(f'page {page} is empty')
            if pages == 0:
                break

        encountered_old_status = False
        for card in cards:
            json_, new = save_status(card)
            if not json_:
                continue
            if new:
                db.parse_and_save_status(json_)
            else:
                encountered_old_status = True
        if update and encountered_old_status:
            break

        page += 1

TIMESTAMP_PATTERN = re.compile(r'date=\\"(?P<timestamp>\d+)000\\"')

def fetch_timestamp(sid, status_url_basename):
    status_url = f'http://weibo.com/{UID}/{status_url_basename}'
    logger.info(f'fetching timestamp for {sid} from {status_url}')
    resp = session.get(
        status_url,
        headers={'Referer': f'http://weibo.com/u/{UID}'},
    )
    assert resp.status_code == 200
    return int(TIMESTAMP_PATTERN.search(resp.text).group('timestamp'))

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
