from . import db_postgresql as db
from os import environ

try:
    USE_DB = environ['USE_DB'] != 'false'
except KeyError:
    USE_DB = False

if USE_DB:
    db.build()
