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


# Support for audio mirroring.
def audio_prefixes():
    if config.values.audio_prefixes:
        prefixes = config.values.audio_prefixes
    else:
        prefixes = [asset_path('audio')]
    prefixes = [f'{prefix}/' if not prefix.endswith('/') else prefix for prefix in prefixes]
    return prefixes


def local_image_path(filename, res):
    return asset_path(f'images/{res}/{filename}')


def sina_image_path(filename, res):
    subdomain = f'ww{hash(filename) % 4 + 1}'
    return f'https://{subdomain}.sinaimg.cn/{res}/{filename}'
