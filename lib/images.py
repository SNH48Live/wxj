#!/usr/bin/env python3

import atexit
import multiprocessing.pool
import random
import subprocess

import requests

from .common import IMAGESDIR, TOOLSDIR, logger

THUMBNAILER = TOOLSDIR / 'thumbnail'

image_processing_pool = None


def ensure_sinaimg(basename):
    for res in ['large', 'thumb180']:
        directory = IMAGESDIR / res
        directory.mkdir(parents=True, exist_ok=True)
        localpath = directory / basename
        if localpath.exists():
            continue
        rand = random.randrange(1, 5)
        url = f'https://ww{rand}.sinaimg.cn/{res}/{basename}'
        logger.info(f'downloading {url}')
        try:
            resp = requests.get(url, stream=True)
            assert resp.status_code == 200
            with open(localpath, 'wb') as fp:
                for chunk in resp.iter_content(16384):
                    fp.write(chunk)
        except Exception:
            logger.error(f'failed to download {url}')
            try:
                localpath.unlink()
            except FileNotFoundError:
                pass

    for res in ['thumb120', 'thumb240', 'thumb360']:
        localpath = IMAGESDIR / res / basename
        if not localpath.exists():
            break
    else:
        # All thumbnails have already been generated
        return
    # Generate thumbnails
    logger.info(f'generating thumbnails for {basename}')
    subprocess.run([THUMBNAILER, basename])


def ensure_sinaimgs(basenames):
    global image_processing_pool
    if image_processing_pool is None:
        image_processing_pool = multiprocessing.pool.Pool()
        # Note that atexit runs registered functions in the
        # reverse order of registration.
        atexit.register(image_processing_pool.join)
        atexit.register(image_processing_pool.close)
    image_processing_pool.map_async(ensure_sinaimg, basenames, chunksize=1)
