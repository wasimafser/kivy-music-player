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
        row['image'] = extract_song_artwork(row['image'], row['id'])

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

    song_data = cursor.fetchone()
    song_data['image'] = extract_song_artwork(song_data['image'], song_data['id'])

    return song_data
