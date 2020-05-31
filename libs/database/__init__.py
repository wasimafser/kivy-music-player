import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect('libs/database/matrix.db')
# con.row_factory = sqlite3.Row
con.row_factory = dict_factory

added_artists = []
added_artist_ids = {}
