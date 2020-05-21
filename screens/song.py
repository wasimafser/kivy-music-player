from kivy.app import MDApp
from kivy.uix.screenmanager import Screen

class SongScreen(Screen):
    loop_status = NumericProperty(0)
    shuffle_status = BooleanProperty(False)
    song_max_length = NumericProperty(0)
    song_current_pos = NumericProperty(0)
    song_path = StringProperty('')
    song = None
    mPlayer = None
    song_state = StringProperty('pause')
    song_name = StringProperty('')

    def convert_seconds_to_min(self, sec):
        val = str(datetime.timedelta(seconds = sec)).split(':')
        return f'{val[1]}:{val[2].split(".")[0]}'

    def go_to_main(self, *args):
        MDApp.get_running_app().sm.current = 'main_screen'

    def compute_average_image_color(self, *args):
        if self.app.now_playing_background != 'artwork-color':
            bg = self.ids.song_screen_bg
            bg.canvas.before.clear()
            return

        pixels_data = self.ids.album_art.texture.pixels
        r_total = 0
        g_total = 0
        b_total = 0

        count = 0
        i = 0

        for p in pixels_data:
            if i == 0:
                r_total += p
            elif i == 1:
                g_total += p
            elif i == 2:
                b_total += p
            elif i == 3:
                count += 1
                i = -1
            i += 1

        r_final = round((r_total/count)/255, 2)
        g_final = round((g_total/count)/255, 2)
        b_final = round((b_total/count)/255, 2)

        self.avg_artwork_color = (r_final, g_final, b_final)
        bg = self.ids.song_screen_bg
        with bg.canvas.before:
            Color(r_final, g_final, b_final)
            Rectangle(size=bg.size, pos=bg.pos)

    def __init__(self, *args, **kwargs):
        super(SongScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.app.bind(now_playing = self.play_song)
        self.app.bind(now_playing_background = self.compute_average_image_color)
        self.play_song()

        self.ids.song_screen_toolbar.remove_notch()

    def play_song(self, *args):
        now_playing = self.app.now_playing
        self.song_path = now_playing['path']
        self.song_name = now_playing['name']

        self.ids.album_art.texture = now_playing['artwork']
        if self.app.config.get('now-playing', 'background') == 'artwork-color':
            Clock.schedule_once(self.compute_average_image_color, 0.5)
        if self.song is not None:
            if platform == 'macosx':
                self.song.stop()
            else:
                self.song.stop()
                self.song.unload()

        if platform == 'android':
            import android_native_media_player
        self.song = SoundLoader.load(self.song_path)

        if self.song:
            self.song_max_length = self.song.length
            self.ids.song_total_length_label.text = self.convert_seconds_to_min(self.song_max_length)
            self.song.play()
            self.loop_status = 1
            self.toggle_loop()
            Clock.schedule_interval(self.manage_song, 1)

    def manage_song(self, *args):
        # print(self.song.get_pos(), self.song.length)
        self.song_current_pos = self.song.get_pos()
        self.ids.song_cur_pos_label.text = self.convert_seconds_to_min(self.song_current_pos)

    def seek_song(self, *args):
        self.song_current_pos = self.ids.song_slider.value
        self.song.seek(self.song_current_pos)

    def toggle_song_play(self, *args):
        if self.song.state == 'play':
            self.song_state = 'play'
            self.song.stop()
        elif self.song.state == 'stop':
            self.song_state = 'pause'
            self.song.play()

    def next_song(self, *args):
        current_song_id = self.app.now_playing['id']
        try:
            self.app.now_playing = self.app.all_songs[current_song_id+1]
        except KeyError:
            self.app.now_playing = self.app.all_songs[0]

    def prev_song(self, *args):
        current_song_id = self.app.now_playing['id']
        try:
            self.app.now_playing = self.app.all_songs[current_song_id-1]
        except KeyError:
            self.app.now_playing = self.app.all_songs[0]

    def toggle_loop(self, *args):
        if self.loop_status == 0:
            self.loop_status = 1
            self.song.loop = True
            if platform == 'android':
                self.song.toggle_loop(True)
        else:
            self.loop_status = 0
            self.song.loop = False
            if platform == 'android':
                self.song.toggle_loop(False)

    def toggle_shuffle(self, *args):
        if self.shuffle_status:
            self.shuffle_status = False
        else:
            self.shuffle_status = True
