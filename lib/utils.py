import urllib.parse

from . import config


def site_path(path):
    if path.startswith('/'):
        path = path[1:]
    return urllib.parse.urljoin(config.values.site_root, path)


def asset_path(path):
    # Always interpret path as relative.
    if path.startswith('/'):
        path = path[1:]
    return site_path(urllib.parse.urljoin('/assets/', path))


def local_image_path(filename, res):
    return asset_path(f'images/{res}/{filename}')


def sina_image_path(filename, res):
    subdomain = f'ww{hash(filename) % 4 + 1}'
    return f'https://{subdomain}.sinaimg.cn/{res}/{filename}'
