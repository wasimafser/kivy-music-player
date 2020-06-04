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

def artist(artist_id):
    with con:
        cursor = con.execute('''
            SELECT *
            FROM artist
            WHERE id = ?
        ''', (artist_id, ))

    artist_data = cursor.fetchone()
    artist_data['image'] = extract_song_artwork(artist_data['image'], f"a_{artist_data['id']}")

    return artist_data

def artist_songs(artist_id):
    with con:
        cursor = con.execute('''
            SELECT
                s.*
            FROM
                songs s
                INNER JOIN song_artist ON song_artist.song_id = s.id
            WHERE
                song_artist.artist_id = ? AND song_artist.artist_type = 1
        ''', (artist_id, ))

    all_data = cursor.fetchall()

    for row in all_data:
        row['image'] = extract_song_artwork(row['image'], f"s_{row['id']}")

    return all_data

def all_albums():
    with con:
        cursor = con.execute('''
            SELECT *
            FROM album
        ''')

    all_data = cursor.fetchall()

    for row in all_data:
        row['image'] = extract_song_artwork(row['image'], f"al_{row['id']}")

    return all_data

def album(album_id):
    with con:
        cursor = con.execute('''
            SELECT *
            FROM album
            WHERE id = ?
        ''', (album_id, ))

    album_data = cursor.fetchone()
    album_data['image'] = extract_song_artwork(album_data['image'], f"al_{album_data['id']}")

    return album_data

def album_songs(album_id):
    with con:
        cursor = con.execute('''
            SELECT
                s.*
            FROM
                songs s
            WHERE
                s.album = ?
        ''', (album_id, ))

    all_data = cursor.fetchall()

    for row in all_data:
        row['image'] = extract_song_artwork(row['image'], f"s_{row['id']}")

    return all_data
