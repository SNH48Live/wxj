#!/usr/bin/env python3

def localimgpath(filename, res):
    return f'/assets/images/{res}/{filename}'

def sinaimgpath(filename, res):
    subdomain = 'ww' + str(sum(map(ord, filename)) % 4 + 1)
    return f'http://{subdomain}.sinaimg.cn/{res}/{filename}'
