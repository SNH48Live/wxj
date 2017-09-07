#!/usr/bin/env python3

import json
import os
import re

from . import config

HERE = os.path.dirname(os.path.realpath(__file__))
DATAFILE = os.path.join(HERE, 'emojis.json')

EMOJIS = {
    'apple': {},
    'pictorial': {},
}

def load():
    if os.path.isfile(DATAFILE):
        with open(DATAFILE) as fp:
            EMOJIS.update(json.load(fp))

load()

def emoji(label):
    if label in EMOJIS['apple']:
        return EMOJIS['apple'][label]
    elif label in EMOJIS['pictorial']:
        filename = EMOJIS['pictorial'][label]
        path = config.asset_path(f'images/emojis/{filename}')
        return f'<img src="{path}" alt="[{label}]">'
    else:
        return f'[{label}]'

EMOJI_PLACEHOLDER = re.compile(r'\[(?P<label>[^\]]+)\]')

def markup_emojis(text):
    return EMOJI_PLACEHOLDER.sub(lambda m: emoji(m.group('label')), text)
