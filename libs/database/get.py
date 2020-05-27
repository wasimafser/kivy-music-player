from libs.database import con

def all_songs():
    with con:
        cursor = con.execute("SELECT * FROM songs")

    return cursor.fetchall()
