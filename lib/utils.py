#!/usr/bin/env python3

from . import config

def localimgpath(filename, res):
    return config.asset_path(f'images/{res}/{filename}')

def sinaimgpath(filename, res):
    subdomain = 'ww' + str(sum(map(ord, filename)) % 4 + 1)
    return f'http://{subdomain}.sinaimg.cn/{res}/{filename}'
