import pathlib
import mutagen
import io
import datetime

from kivy.core.image import Image as CoreImage
from kivy.utils import platform

from libs.media.mediafile import MediaFile
from libs.database import con

with con:
    con.execute('''CREATE TABLE IF NOT EXISTS artist(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR UNIQUE,
                    image BLOB
    );''')

with con:
    con.execute('''CREATE TABLE IF NOT EXISTS album(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR UNIQUE,
                    artist INTEGER,
                    image BLOB,
                    FOREIGN KEY (artist) REFERENCES artist (id)
    );''')

with con:
    con.execute('''CREATE TABLE IF NOT EXISTS songs(
                    id integer primary key AUTOINCREMENT,
                    name varchar UNIQUE,
                    length varchar,
                    extension varchar,
                    path varchar,
                    album INTEGER,
                    image BLOB,
                    FOREIGN KEY (album) REFERENCES album (id)
    );''')

def extract_song_artwork(song_path, *args):
    try:
        song_file = mutagen.File(song_path)
        if song_path.suffix == '.mp3':
            artwork_data = song_file.tags.getall('APIC')[0].data
            # artwork = CoreImage(io.BytesIO(artwork_data), ext='png', mipmap=True).texture
        elif song_path.suffix == '.m4a':
            artwork_data = song_file.tags['covr'][0]
            # artwork = CoreImage(io.BytesIO(artwork_data), ext='png', mipmap=True).texture
        else:
            artwork_data = open('artwork/default.jpg', 'rb').read()
            # io.BytesIO()
            # artwork = CoreImage(artwork_data, ext='png', mipmap=True).texture
    except Exception as e:
        print(e)
        # print("has error", e)
        artwork_data = open('artwork/default.jpg', 'rb').read()
        # artwork_data = io.BytesIO()
        # artwork = CoreImage(artwork_data, ext='png', mipmap=True).texture

    return artwork_data

def convert_seconds_to_min(sec):
    if sec == 0:
        return '00:00'
    val = str(datetime.timedelta(seconds = sec)).split(':')
    return f'{val[1]}:{val[2].split(".")[0]}'

def initialize(config):
    with con:
        cursor = con.execute("SELECT path FROM songs")
    paths_list = cursor.fetchall()
    paths = [path['path'] for path in paths_list]

    from libs.media.mediafile import MediaFile

    folders = str(config.get('search-paths', 'folders')).split(',')
    if '/' in folders:
        folders.remove('/')

    for folder in folders:
        for format in ["mp3", "aac", "3gp", "flac", "mkv", "wav", "ogg", "m4a"]:
            for file in pathlib.Path(folder).rglob(f'*.{format}'):
                path = str(file)
                if path in paths:
                    print("SKIPPING")
                    continue

                audio_file = MediaFile(file)

                if platform == 'win':
                    path = path.replace('/', '\\')

                info = {
                    'album': audio_file.tags['album'],
                    'artist': audio_file.tags['artist'],
                    'path': path,
                    'name': audio_file.tags['name'] if audio_file.tags['name'] != 'None' else file.stem,
                    'extension': file.suffix,
                    'artwork': extract_song_artwork(file),
                    'length': convert_seconds_to_min(audio_file.info['length'])
                }

                try:
                    with con:
                        cursor = con.execute("INSERT INTO artist(name) VALUES(?)", (info['artist'], ))
                    artist_id = cursor.lastrowid
                except Exception as e:
                    with con:
                        cursor = con.execute("SELECT id FROM artist WHERE name = ?", (info['artist'], ))
                    artist_id = cursor.fetchone()['id']

                try:
                    with con:
                        cursor = con.execute("INSERT INTO album(name, artist) VALUES(?, ?)", (info['album'], artist_id, ))
                    album_id = cursor.lastrowid
                except Exception as e:
                    with con:
                        cursor = con.execute("SELECT id from album WHERE name = ?", (info['album'], ))
                    album_id = cursor.fetchone()['id']

                try:
                    with con:
                        con.execute("INSERT INTO songs(name, length, extension, path, album, image) VALUES(?, ?, ?, ?, ?, ?)", (info['name'], info['length'], info['extension'], info['path'], album_id, info['artwork'], ))
                except:
                    pass
