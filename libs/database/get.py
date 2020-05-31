from libs.database import con

from kivy.core.image import Image as CoreImage
import io

def extract_song_artwork(image_data, song_id):
    artwork = CoreImage(io.BytesIO(image_data), ext='png', filename=f"{song_id}.png", mipmap=True).texture
    return artwork

def all_songs():
    with con:
        cursor = con.execute('''
            SELECT
                s.*,
                album.name as album,
                artist.name as artist
            FROM
                songs s
                INNER JOIN album ON s.album = album.id
                INNER JOIN artist ON album.artist = artist.id
        ''')

    all_data = cursor.fetchall()

    for row in all_data:
        row['image'] = extract_song_artwork(row['image'], f"s_{row['id']}")

    return all_data

def song(id):
    with con:
        cursor = con.execute('''
            SELECT
                s.*,
                album.name as album,
                artist.name as artist
            FROM
                songs s
                INNER JOIN album ON s.album = album.id
                INNER JOIN artist ON album.artist = artist.id
            WHERE
                s.id = ?
        ''', (id, ))

        cursor_1 = con.execute('''
            SELECT
                artist.name as artist,
                sa.artist_type as type
            FROM
                song_artist sa
                INNER JOIN artist ON sa.artist_id = artist.id
            WHERE
                sa.song_id = ?
        ''', (id, ))

    song_artist_data = cursor_1.fetchall()

    song_data = cursor.fetchone()
    for artist in song_artist_data:
        if artist['type'] == 1:
            song_data['artist'] = artist['artist']
        else:
            song_data['artist'] += f" & {artist['artist']}"
    song_data['image'] = extract_song_artwork(song_data['image'], f"s_{song_data['id']}")

    return song_data

def most_listened_songs():
    with con:
        cursor = con.execute('''
            SELECT
                s.*,
                album.name as album,
                artist.name as artist
            FROM
                songs s
                INNER JOIN album ON s.album = album.id
                INNER JOIN artist ON album.artist = artist.id
            WHERE
                s.times_listened > 2 AND
                s.times_listened > (SELECT MAX(s.times_listened)
                                    FROM songs s)/2
        ''')

    all_data = cursor.fetchall()

    for row in all_data:
        row['image'] = extract_song_artwork(row['image'], f"s_{row['id']}")

    return all_data

def all_artists():
    with con:
        cursor = con.execute('''
            SELECT *
            FROM artist
            WHERE image NOT NULL
        ''')

    all_data = cursor.fetchall()

    for row in all_data:
        row['image'] = extract_song_artwork(row['image'], f"a_{row['id']}")

    return all_data
