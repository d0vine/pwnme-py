import sqlite3
from flask import g

DATABASE = 'huehuehue.db'

'''
def sqlite(func):
    def wrapped(*args, **kwargs):
        db_conn = sqlite3.connect(DATABASE)
        return func(db_conn.cursor(), *args, **kwargs)

    return wrapped
'''

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

