#!/usr/bin/env python3

import json
import re

from . import utils
from .common import DATADIR

DATAFILE = DATADIR / 'emojis.json'

EMOJIS = {
    'apple': {},
    'pictorial': {},
}

def load():
    if DATAFILE.exists():
        with open(DATAFILE) as fp:
            EMOJIS.update(json.load(fp))

load()

def emoji(label):
    if label in EMOJIS['apple']:
        return EMOJIS['apple'][label]
    elif label in EMOJIS['pictorial']:
        filename = EMOJIS['pictorial'][label]
        path = utils.asset_path(f'images/emojis/{filename}')
        return f'<img src="{path}" alt="[{label}]">'
    else:
        return f'[{label}]'

EMOJI_PLACEHOLDER = re.compile(r'\[(?P<label>[^\]]+)\]')

def markup_emojis(text):
    return EMOJI_PLACEHOLDER.sub(lambda m: emoji(m.group('label')), text)
