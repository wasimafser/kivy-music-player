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
        self.quitted = False
        self._state = ''
        self.state = 'stop'
        super(SoundAndroidPlayer, self).__init__(**kwargs)

    def __del__(self):
        self.unload()

    def _player_callback(self, selector, value):
        if self._mediaplayer is None:
            return
        if selector == 'quit':
            def close(*args):
                self.quitted = True
                self.unload()
            Clock.schedule_once(close, 0)
        elif selector == 'eof':
            Clock.schedule_once(self._do_eos, 0)

    def load(self):
        self.unload()
        self._mediaplayer = MediaPlayer()
        self._mediaplayer.setAudioStreamType(AudioManager.STREAM_MUSIC);
        self._mediaplayer.setDataSource(self.filename)
        self._mediaplayer.prepare()
        self._state = 'paused'

    def unload(self):
        if self._mediaplayer:
            self._mediaplayer = None
        self._state = ''
        self.state = 'stop'
        self.quitted = False

    def play(self):
        if self._state == 'playing':
            super(SoundAndroidPlayer, self).play()
            return
        if not self._mediaplayer:
            self.load()
        self._mediaplayer.start()
        self._state = 'playing'
        self.state = 'play'
        super(SoundAndroidPlayer, self).play()

    def stop(self):
        if self._mediaplayer and self._state == 'playing':
            # self._mediaplayer.reset()
            self._mediaplayer.pause()
            self._state = 'paused'
            self.state = 'stop'
        super(SoundAndroidPlayer, self).stop()

    def seek(self, position):
        if self._mediaplayer is None:
            return
        self._mediaplayer.seekTo(float(position*1000.))

    def get_pos(self):
        if self._mediaplayer is not None:
            return self._mediaplayer.getCurrentPosition() / 1000.
        # return super(SoundAndroidPlayer, self).get_pos()
        return 0

    def on_volume(self, instance, volume):
        if self._mediaplayer is not None:
            volume = float(volume)
            self._mediaplayer.setVolume(volume, volume)

    def _get_length(self):
        if self._mediaplayer is not None:
            return self._mediaplayer.getDuration() / 1000.
        return super(SoundAndroidPlayer, self)._get_length()

    def _do_eos(self, *args):
        if not self.loop:
            self.stop()
        else:
            self.seek(0.)

SoundLoader.register(SoundAndroidPlayer)
