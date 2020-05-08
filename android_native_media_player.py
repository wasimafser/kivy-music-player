from kivy.core.audio import Sound, SoundLoader
from jnius import autoclass
MediaPlayer = autoclass("android.media.MediaPlayer")
FileInputStream = autoclass("java.io.FileInputStream")
AudioManager = autoclass("android.media.AudioManager")

class SoundAndroidPlayer(Sound):
    @staticmethod
    def extensions():
        return ("mp3", "mp4", "aac", "3gp", "flac", "mkv", "wav", "ogg")

    def __init__(self, **kwargs):
        self._mediaplayer = None
        self._state = ''
        self.state = 'stop'
        super(SoundAndroidPlayer, self).__init__(**kwargs)

    def load(self):
        print("LOADING FROM NATIVE ANDROID PLAYER")
        self.unload()
        self._mediaplayer = MediaPlayer()
        self._mediaplayer.setAudioStreamType(AudioManager.STREAM_MUSIC);
        self._mediaplayer.setDataSource(self.filename)
        self._mediaplayer.prepare()
        self._state = 'paused'

    def unload(self):
        self.stop()
        self._mediaplayer = None
        self._state = ''
        self.state = 'stop'

    def play(self):
        if not self._mediaplayer:
            return
        self._state = 'playing'
        self.state = 'play'
        self._mediaplayer.start()
        super(SoundAndroidPlayer, self).play()

    def stop(self):
        if not self._mediaplayer:
            return
        elif self._state == 'playing':
            # self._mediaplayer.reset()
            self._mediaplayer.pause()
            self._state = 'paused'
            self.state = 'stop'
        super(SoundAndroidPlayer, self).stop()

    def seek(self, position):
        print(position)
        if not self._mediaplayer:
            return
        self._mediaplayer.seekTo(float(position/1000), 2)

    def get_pos(self):
        if self._mediaplayer:
            return self._mediaplayer.getCurrentPosition() / 1000.
        return super(SoundAndroidPlayer, self).get_pos()

    def on_volume(self, instance, volume):
        if self._mediaplayer:
            volume = float(volume)
            self._mediaplayer.setVolume(volume, volume)

    def _get_length(self):
        if self._mediaplayer:
            return self._mediaplayer.getDuration() / 1000.
        return super(SoundAndroidPlayer, self)._get_length()

SoundLoader.register(SoundAndroidPlayer)
