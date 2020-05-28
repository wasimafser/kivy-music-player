from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen

from kivy.lang.builder import Builder
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.utils import platform
from kivy.core.audio import Sound, SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import datetime

Builder.load_string('''
<SongScreen>:
    name: 'song_screen'
    BoxLayout:
        orientation: 'vertical'
        id: song_screen_bg
        spacing: dp(10)

        BoxLayout:
            size_hint_y: 0.05

        MDCard:
            size_hint: 0.5, 0.5
            pos_hint: {"center_x": .5, "center_y": .5}
            # canvas:
            #     Color:
            #         rgba: (0, 0, 0, 0)
            #     Rectangle:
            #         size: self.size
            #         pos: self.pos

            FitImage:
                size_hint: 1, 1
                id: album_art

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            # canvas.before:
            #     Color:
            #         rgba: (0, 0, 1, 0.5)
            #     Rectangle:
            #         size: self.size
            #         pos: self.pos

            MDLabel:
                text: root.song_name
                halign: 'center'
                theme_text_color: 'Primary'

            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: 0.05

                MDLabel:
                    id: song_cur_pos_label
                    size_hint: 0.2, 1
                    halign: "center"
                    theme_text_color: 'Primary'
                MDSlider:
                    id: song_slider
                    min: 0
                    max: root.song_max_length
                    value: root.song_current_pos
                    hint: False
                    on_touch_up: if self.collide_point(*args[1].pos): root.seek_song()
                MDLabel:
                    id: song_total_length_label
                    size_hint: 0.2, 1
                    halign: "center"
                    theme_text_color: 'Primary'

            BoxLayout:
                MDBottomAppBar:
                    MDToolbar:
                        id: song_screen_toolbar
                        icon: root.song_state
                        type: 'bottom'
                        left_action_items: [["repeat-off" if root.loop_status == 0 else "repeat-once", lambda x: root.toggle_loop()], ["skip-previous", lambda x: root.prev_song()]]
                        right_action_items: [["skip-next", lambda x: root.next_song()], ["shuffle-disabled" if not root.shuffle_status else "shuffle-variant", lambda x: root.toggle_shuffle()]]
                        on_action_button: root.toggle_song_play()
                        mode: 'center'
''')

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

    songs_counter = NumericProperty(0)
    ADMOB_LOADED_PREVIOUSLY = BooleanProperty(False)
    AMAZON_LOADED_PREVIOUSLY = BooleanProperty(False)

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

    def on_songs_counter(self, instance, value, *args):
        if value % 3 == 0 and platform == 'android':
            if not self.AMAZON_LOADED_PREVIOUSLY:
                self.app.InterstitialAd.loadAd()
            elif not self.ADMOB_LOADED_PREVIOUSLY:
                self.app.ads.request_interstitial()
        else:
            pass

    def __init__(self, *args, **kwargs):
        super(SongScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.app.bind(now_playing = self.play_song)
        self.app.bind(now_playing_background = self.compute_average_image_color)
        self.play_song()

        self.ids.song_screen_toolbar.remove_notch()

    def play_song(self, *args):
        # SHOW AD ON PAUSE AND IF NUMBER OF SONGS PLAYED IS MULTIPLE Of 3
        if self.songs_counter % 3 == 0 and platform == 'android':
            # LOAD THE ADD WHICH IS AVAILABLE AND THE OTHER LATER
            if self.app.InterstitialAd.isReady() and not self.AMAZON_LOADED_PREVIOUSLY:
                self.app.InterstitialAd.showAd()
                self.AMAZON_LOADED_PREVIOUSLY = True
                self.ADMOB_LOADED_PREVIOUSLY = False
            elif self.app.ads.is_interstitial_loaded() and not self.ADMOB_LOADED_PREVIOUSLY:
                self.app.ads.show_interstitial()
                self.ADMOB_LOADED_PREVIOUSLY = True
                self.AMAZON_LOADED_PREVIOUSLY = False
            else:
                self.AMAZON_LOADED_PREVIOUSLY = False
                print("BOTH ADS NOT LOADED")

        self.songs_counter += 1

        now_playing = self.app.now_playing
        self.song_path = now_playing['path']
        self.song_name = now_playing['name']

        self.ids.album_art.texture = now_playing['image']
        if self.app.config.get('now-playing', 'background') == 'artwork-color':
            Clock.schedule_once(self.compute_average_image_color, 0.5)
        if self.song is not None:
            if platform == 'macosx' or platform == 'win':
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
                try:
                    self.song.toggle_loop(True)
                except Exception as e:
                    print(e)
        else:
            self.loop_status = 0
            self.song.loop = False
            if platform == 'android':
                try:
                    self.song.toggle_loop(False)
                except Exception as e:
                    print(e)

    def toggle_shuffle(self, *args):
        if self.shuffle_status:
            self.shuffle_status = False
        else:
            self.shuffle_status = True
