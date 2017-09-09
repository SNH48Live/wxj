import json
import os
import re

from .common import APIDIR


def load_status(status_id):
    filesystem_path = APIDIR / f'{status_id}.json'
    with open(filesystem_path) as fp:
        return json.load(fp)


STATUS_JSON_FILE = re.compile(r'^(?P<status_id>\d+)\.json$')


def list_existing_status_ids():
    status_ids = []
    for filename in os.listdir(APIDIR):
        m = STATUS_JSON_FILE.match(filename)
        if m:
            status_ids.append(m.group('status_id'))
    return status_ids
