import mutagen
import pathlib

class MediaFile(object):

    def __init__(self, path):
        # super(MediaFile, self).__init__(path)
        self.tags = {
            'name': 'None',
            'album': 'None',
            'artist': 'None',
            'album_artist': 'None',
            'genre': 'None'
        }

        self.info = {
            'length': 0
        }

        try:
            audio_file = mutagen.File(path)
        except Exception as e:
            print(e)
            return

        self.read_tags(path, audio_file)
        self.read_info(path, audio_file)

        # name = None
        # album = None
        # artist = None
        # album_artist = None
        # genre = None

    def read_tags(self, file, audio_file):
        if file.suffix == '.mp3':
            self.tags['name'] = audio_file.tags.get('TIT2', ['None'])[0]
            self.tags['album'] = audio_file.tags.get('TALB', ['None'])[0]
            self.tags['genre'] = audio_file.tags.get('TCON', ['None'])[0]
        elif file.suffix == '.m4a':
            self.tags['name'] = audio_file.tags.get('\xa9nam', ['None'])[0]
            self.tags['album'] = audio_file.tags.get('\xa9alb', ['None'])[0]
            self.tags['artist'] = audio_file.tags.get('\xa9ART', ['None'])[0]
            self.tags['album_artist'] = audio_file.tags.get('aART', ['None'])[0]
            self.tags['genre'] = audio_file.tags.get('\xa9gen', ['None'])[0]

    def read_info(self, file, audio_file):
        self.info['length'] = audio_file.info.length
