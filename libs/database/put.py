from libs.database import con

def update_times_listened(song_id):
    with con:
        con.execute('''
            UPDATE songs
            SET times_listened = times_listened + 1
            WHERE id = ?
        ''', (song_id, ))
