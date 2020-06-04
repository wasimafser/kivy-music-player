import pathlib
import mutagen
import io
import datetime
import re
import sqlite3

from kivy.core.image import Image as CoreImage
from kivy.utils import platform

from libs.media.mediafile import MediaFile
from libs.database import con, added_artists, added_artist_ids
from libs.api import spotify

with con:
    con.execute('''CREATE TABLE IF NOT EXISTS artist(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spotify_id VARCHAR UNIQUE,
                    name VARCHAR UNIQUE,
                    image BLOB
    );''')

with con:
    con.execute('''CREATE TABLE IF NOT EXISTS album(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spotify_id VARCHAR UNIQUE,
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
                    times_listened INTEGER DEFAULT 0,
                    FOREIGN KEY (album) REFERENCES album (id)
    );''')

with con:
    con.execute('''
        CREATE TABLE IF NOT EXISTS artist_type(
            id integer primary key AUTOINCREMENT,
            type VARCHAR
        );
    ''')

    con.executemany('''
        INSERT INTO artist_type(type) VALUES(?);
    ''', [('MAIN', ), ('OTHER', ), ])

with con:
    con.execute('''
        CREATE TABLE IF NOT EXISTS song_artist(
            id integer primary key AUTOINCREMENT,
            song_id INTEGER REFERENCES songs(id),
            artist_id INTEGER REFERENCES artist(id),
            artist_type INTEGER REFERENCES artist_type(id)
        );
    ''')

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
                    'album_artist': audio_file.tags['album_artist'],
                    'path': path,
                    'name': audio_file.tags['name'] if audio_file.tags['name'] != 'None' else file.stem,
                    'extension': file.suffix,
                    'artwork': extract_song_artwork(file),
                    'length': convert_seconds_to_min(audio_file.info['length'])
                }

                try:
                    names_separator = re.findall('[^A-Za-z0-9 ]', info['artist'])
                    # print(result)
                except Exception as e:
                    print(e)

                # IF ALBUM ARTIST AND ARTIST ARE SAME THEN SAVE ONCE
                values = []
                main_artist = None
                if info['album_artist'].lower() == info['artist'].lower():
                    values.append(info['album_artist'])
                else:
                    if info['album_artist'] != 'Unknown':
                        values.append(info['album_artist'])
                        main_artist = info['album_artist']
                    if info['artist'] != 'Unknown':
                        if names_separator:
                            values.extend([artist.strip() for artist in info['artist'].split(names_separator[0]) if artist.strip() not in values])
                        else:
                            values.append(info['artist'])

                with con:
                    for artist in values:
                        if artist not in added_artists:
                            added_artists.append(artist)
                            artist_info = {
                                'spotify_id': None,
                                'image': None
                            }
                            if artist != 'Unknown':
                                pass
                                artist_info = spotify.get_artist_info(artist, search=True)
                            try:
                                cursor = con.execute('''
                                    INSERT INTO artist(name, spotify_id, image)
                                    VALUES(?, ?, ?)
                                    ''', (artist, artist_info['spotify_id'], artist_info['image'],))
                                added_artist_ids[artist] = cursor.lastrowid
                                print(added_artist_ids)
                            except sqlite3.IntegrityError as e:
                                print(e)
                                continue

                with con:
                    if not main_artist:
                        # GET THE VALUE OF FIRST ARTIST HOPING THAT IT WOULD BE THE MAIN ARTIST
                        main_artist = values[0]
                    cursor = con.execute("SELECT id FROM artist WHERE name = ?", (main_artist, ))
                artist_id = cursor.fetchone()['id']

                try:
                    with con:
                        album_info = {
                            'spotify_id': None,
                            'image': None
                        }
                        album_info = spotify.get_album_info(info['album'], search=True)
                        cursor = con.execute("INSERT INTO album(name, artist, spotify_id, image) VALUES(?, ?, ?, ?)", (info['album'], artist_id, album_info['spotify_id'], album_info['image']))
                    album_id = cursor.lastrowid
                except sqlite3.IntegrityError:
                    with con:
                        cursor = con.execute("SELECT id from album WHERE name = ?", (info['album'], ))
                    album_id = cursor.fetchone()['id']

                with con:
                    cursor = con.execute("INSERT INTO songs(name, length, extension, path, album, image) VALUES(?, ?, ?, ?, ?, ?)", (info['name'], info['length'], info['extension'], info['path'], album_id, info['artwork'], ))
                    song_id = cursor.lastrowid

                    for artist in values:
                        artist_type = 2
                        if artist == main_artist:
                            artist_type = 1
                        con.execute("INSERT INTO song_artist(song_id, artist_id, artist_type) VALUES(?, ?, ?)", (song_id, added_artist_ids[artist], artist_type))
