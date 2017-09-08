#!/usr/bin/env python3

import os
import peewee

from .common import DATADIR

DBPATH = DATADIR / 'data.db'
db = peewee.SqliteDatabase(os.fspath(DBPATH))


class Status(peewee.Model):
    status_id = peewee.IntegerField(unique=True)
    created_at = peewee.IntegerField()
    body = peewee.TextField()
    images = peewee.TextField()

    repost = peewee.BooleanField(default=False)
    orig_body = peewee.TextField(default='')
    orig_images = peewee.TextField(default='')

    class Meta:
        database = db


db.connect()
db.create_table(Status, safe=True)
