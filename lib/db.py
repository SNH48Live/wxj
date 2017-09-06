#!/usr/bin/env python3

import html
import os
import json
import re

import bs4
import peewee

from . import api, config, emojis, shortlinks
from .logger import logger

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DBPATH = os.path.join(ROOT, 'data.db')

db = peewee.SqliteDatabase(DBPATH)

class Status(peewee.Model):
    sid = peewee.IntegerField(unique=True)
    created_at = peewee.IntegerField()
    url = peewee.TextField()
    body = peewee.TextField()
    images = peewee.TextField()

    repost = peewee.BooleanField(default=False)
    orig_body = peewee.TextField(default='')
    orig_images = peewee.TextField(default='')

    class Meta:
        database = db

db.connect()
db.create_table(Status, safe=True)

def images_from_mblog(mblog):
    if 'pics' in mblog:
        return [os.path.basename(pic['url']) for pic in mblog['pics']]
    else:
        return []

REPOST_MENTION = re.compile(r'(//<a href=\'http://m.weibo.cn/n/[^>]+\'>@[^<]+</a>):')

def flatten_status_body(body):
    # Transform repost mention colons first
    body = REPOST_MENTION.sub(lambda m: f'{m.group(1)}：', body)
    soup = bs4.BeautifulSoup(body, 'html.parser')
    text = ''
    children = soup.children
    for e in children:
        if isinstance(e, bs4.NavigableString):
            text += html.escape(e)
        else:
            if e.name == 'a':
                href = e['href']
                if (href.startswith('http://m.weibo.cn/n/') or
                    href.startswith('http://m.weibo.cn/k/')):
                    text += f'<b>{html.escape(e.text)}</b>'
                elif e.span is not None and 'url-icon' in e.span['class']:
                    ne = next(children)
                    assert ne.name == 'span' and 'surl-text' in ne['class']

                    shorturl = e['data-url']
                    url = shortlinks.resolve(shorturl)
                    desc = ne.text

                    text += f'<a href="{url}" data-canonical-href="{shorturl}" target="_blank">{html.escape(desc)}</a>'
                else:
                    text += str(e)
            elif e.name == 'i' and 'face' in e['class']:
                assert e.text.startswith('[') and e.text.endswith(']')
                label = e.text[1:-1]
                emojis.save_mweibocn_emoji(label, e['class'])
                text += e.text
            elif e.name == 'span' and 'url-icon' in e['class']:
                emojiurl = e.img['src']
                localurl = emojis.resolve_linked_emoji(emojiurl)
                text += f'<img src="{localurl}">'
            elif e.name == 'br':
                text += '<br>'
            else:
                text += str(e)
    return text

MWEIBOCN_STATUS_LINK = re.compile(r'^https?://m\.weibo\.cn/status/(?P<basename>\w+)(\?.*)?')
INCOMPLETE_STATUS_PATTERN = re.compile(r'<a href="/status/(?P<sid>\d+)">全文</a>')

def parse_and_save_status(json_):
    status = {}

    print(json_['scheme'])
    url_basename = MWEIBOCN_STATUS_LINK.match(json_['scheme']).group('basename')
    status['url'] = f'http://weibo.com/{config.uid}/{url_basename}'

    mblog = json_['mblog']
    sid = mblog['id']

    status['created_at'] = mblog['_created_at']
    if INCOMPLETE_STATUS_PATTERN.search(mblog['text']):
        # Expand to complete status
        mblog['text'] = api.resolve_complete_status(sid)
    status['body'] = flatten_status_body(mblog['text']).rstrip('\u200b')
    status_images = images_from_mblog(mblog)
    for filename in status_images:
        api.ensure_sinaimg(filename)
    status['images'] = '\n'.join(status_images)

    if not status['body']:
        # An auto status like this birthday status:
        # http://weibo.com/3053424305/EpCL9pDQf
        return

    if 'retweeted_status' in mblog:
        status['repost'] = True
        retweeted_status = mblog['retweeted_status']
        orig_body = retweeted_status['text']
        m = INCOMPLETE_STATUS_PATTERN.search(orig_body)
        if m:
            orig_body = api.resolve_complete_status(m.group('sid'))
        if retweeted_status['user'] is not None:
            orig_author = retweeted_status['user']['screen_name']
            status['orig_body'] = f'<b>{orig_author}：</b>{flatten_status_body(orig_body)}'
            orig_status_images = images_from_mblog(retweeted_status)
            for filename in orig_status_images:
                api.ensure_sinaimg(filename)
            status['orig_images'] = '\n'.join(orig_status_images)
        else:
            status['orig_body'] = '原状态已被删除。'

    status, new = Status.get_or_create(sid=sid, defaults=status)
    if new:
        logger.info(f'inserted status {sid} into database')

def parse_and_save_all_existing_statuses():
    for sid in api.list_existing_sids():
        parse_and_save_status(api.load_status(sid))

def filter_statuses(statuses):
    # Filter out live streaming feeds
    statuses = [s for s in statuses if not 'href="http://h5.snh48.com/appshare/memberLiveShare' in s.body]
    return statuses
