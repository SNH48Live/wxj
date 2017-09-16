import html
import json
import os
import re
import urllib.parse

import arrow

from . import api, config, images, shortlinks
from .common import APIDIR, logger
from .db import Status


def parse_status_images(status):
    if 'pic_urls' in status:
        status_images = [os.path.basename(url) for url in status['pic_urls']]
        if config.values.local_images:
            images.ensure_sinaimgs(status_images)
        return '\n'.join(status_images)
    else:
        return ''


MENTION = re.compile(r'(//)?(@[^:：\s]+)([:：])?')


def mention_repl(m):
    repost_mention_pre = m.group(1)
    mention = m.group(2)
    quoted_screen_name = urllib.parse.quote(mention[1:])
    repost_mention_post = m.group(3)
    marked_up_mention = f'<a href="https://m.weibo.cn/n/{quoted_screen_name}" target="_blank">{mention}</a>'  # noqa
    if repost_mention_pre and repost_mention_post:
        # A repost mention like '//@SNH48-王晓佳:'
        # We replace the ASCII colon with a FULLWIDTH COLON (U+FF1A).
        return f'//{marked_up_mention}：'
    else:
        return marked_up_mention


TAG = re.compile(r'#([^#\s]+)#')


def tag_repl(m):
    tag = m.group(1)
    quoted_tag = urllib.parse.quote(tag)
    return f'<a href="https://m.weibo.cn/k/{quoted_tag}" target="_blank">#{tag}#</a>'


TCN_LINK = re.compile(r'http://t\.cn/\w+')


def tcn_link_repl(m):
    shorturl = m.group(0)
    url = shortlinks.resolve(shorturl)
    display = shortlinks.display_url(url)
    return f'<a href="{url}" data-canonical-href="{shorturl}" target="_blank">{html.escape(display)}</a>'  # noqa


def get_longtext(status_id):
    if get_longtext.longtexts is None:
        with open(APIDIR / 'longtext.json') as fp:
            get_longtext.longtexts = json.load(fp)

    return get_longtext.longtexts.get(status_id)


get_longtext.longtexts = None


NEEDS_EXPANSION = re.compile(r'^(?P<shortened>.*)\.\.\.全文： http://m\.weibo\.cn/\d+/(?P<status_id>\d+)\s*\u200b?$', re.S)  # noqa


def markup_status_body(body):
    m = NEEDS_EXPANSION.match(body)
    if m:
        longtext = get_longtext(m.group('status_id'))
        if longtext:
            body = longtext
        else:
            # Long text not available
            body = m.group('shortened') + '……'
    body = MENTION.sub(mention_repl, body)
    body = TAG.sub(tag_repl, body)
    body = TCN_LINK.sub(tcn_link_repl, body)
    return body


MWEIBOCN_STATUS_LINK = re.compile(r'^https?://m\.weibo\.cn/status/(?P<basename>\w+)(\?.*)?')


def parse_and_save_status(json_):
    status = {}
    status_id = int(json_['mid'])
    status['created_at'] = int(arrow.get(json_['created_at'], 'YYYY-MM-DD HH:mm:ss',
                                         tz='Asia/Shanghai').timestamp)
    # TODO: if truncated, resolve complete status
    status['body'] = markup_status_body(json_['text'])
    status['images'] = parse_status_images(json_)

    if not status['body']:
        # An auto status like this birthday status:
        # http://weibo.com/3053424305/EpCL9pDQf
        return

    if 'retweeted_status' in json_:
        status['repost'] = True
        retweeted_status = json_['retweeted_status']
        if retweeted_status and 'text' in retweeted_status:
            try:
                orig_author = retweeted_status['user']['screen_name']
            except TypeError:
                # api/3991289312027273.json has "user": [] for whatever reason
                orig_author = '未知用户'
            # TODO: if truncated, resolve complete status
            orig_body = markup_status_body(retweeted_status['text'])
            status['orig_body'] = f'<b>{orig_author}：</b>{orig_body}'
            status['orig_images'] = parse_status_images(retweeted_status)
        else:
            status['orig_body'] = '原状态已被删除。'

    status, new = Status.get_or_create(status_id=status_id, defaults=status)
    if new:
        logger.info(f'inserted status {status_id} into database')


def parse_and_save_all_existing_statuses():
    for status_id in api.list_existing_status_ids():
        parse_and_save_status(api.load_status(status_id))
