#!/usr/bin/env python3

import pathlib
import sys

import yaml

from .common import ROOT, logger


class Config(object):
    def __init__(self):
        self.site_root = None
        self.build_dir = None
        self.local_images = None
        self.statuses_per_page = None


values = Config()


def load(config_file):
    config_file = pathlib.Path(config_file)
    if not config_file.is_absolute():
        config_file = ROOT / config_file
    if not config_file.is_file():
        logger.error(f'configuration file {config_file} does not exist')
        sys.exit(1)

    logger.debug(f'loading configurations from {config_file}')
    with open(config_file) as fp:
        config = yaml.load(fp.read())

    values.site_root = config.get('site_root', '/')
    values.build_dir = pathlib.Path(config.get('build_dir', 'public'))
    if not values.build_dir.is_absolute():
        values.build_dir = ROOT / values.build_dir
    values.local_images = config.get('local_images', True)
    values.statuses_per_page = config.get('statuses_per_page', 20)
