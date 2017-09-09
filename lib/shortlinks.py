import atexit
import json
import re

import requests

from .common import DATADIR, logger

DATAFILE = DATADIR / 'shortlinks.json'
MAPPING = {}


def load():
    if DATAFILE.exists():
        with open(DATAFILE) as fp:
            MAPPING.update(json.load(fp))


load()


def expand(shorturl):
    logger.info(f'expanding {shorturl}')
    try:
        longurl = requests.head(shorturl).headers['Location']
        assert longurl != shorturl
        MAPPING[shorturl] = longurl
        return longurl
    except Exception:
        logger.error(f'failed to expand {shorturl}')
        return shorturl


def resolve(shorturl):
    return MAPPING[shorturl] if shorturl in MAPPING else expand(shorturl)


URL_STRIP_BOILERPLATE = re.compile(r'^https?://(www\.)?(?P<interesting>.*)')
# Target length of the display version of an expanded t.cn URL
LINK_DISPLAY_LENGTH = 20


def display_url(url):
    # Target a length of LINK_DISPLAY_LENGTH characters
    m = URL_STRIP_BOILERPLATE.match(url)
    s = m.group('interesting')
    if len(s) <= LINK_DISPLAY_LENGTH:
        return s
    else:
        return s[:LINK_DISPLAY_LENGTH - 3] + '...'


def persist():
    logger.info('persisting shortlinks')
    if not MAPPING:
        logger.warning('not persisting because there\'s no data to persist; '
                       'something might be wrong!')
        return
    with open(DATAFILE, 'w') as fp:
        json.dump(MAPPING, fp, indent=2, sort_keys=True)


atexit.register(persist)
