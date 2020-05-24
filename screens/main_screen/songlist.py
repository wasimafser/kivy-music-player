from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBody, IRightBody, IRightBodyTouch
from kivymd.utils.fitimage import FitImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton

from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.metrics import Metrics
from kivy.utils import platform

import datetime

Builder.load_string('''
<SongItem>:
    font_style: 'OpenSans'
    divider: 'Full'
    on_size:
        self.ids._right_container.width = right_widgets.width
        self.ids._right_container.x = right_widgets.width
    AlbumArtLeftWidget:
        id: artwork_thumb

    RightWidgets:
        id: right_widgets
        MDLabel:
            id: audio_length
            font_style: 'OpenSans'
            theme_text_color: 'Secondary'

<SongListScreen>:
    BoxLayout:
        orientation: "vertical"

        ScrollView:
            MDList:
                id: songs_list
''')

class RightWidgets(IRightBodyTouch, MDBoxLayout):
    adaptive_width = True

    def __init__(self, *args, **kwargs):
        super(RightWidgets, self).__init__(*args, **kwargs)

        Clock.schedule_once(self.init_widgets)

    def init_widgets(self, *args):
        if platform not in ['android', 'ios']:
            self.add_widget(
                MDIconButton(
                    icon= 'play',
                    on_release= self.switch_to_song_screen
                )
            )

    def switch_to_song_screen(self, *args):
        app = MDApp.get_running_app()
        app.now_playing = app.all_songs[self.parent.parent.song_id]

        sm = app.sm
        screen_name = 'song_screen'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            from screens.song import SongScreen
            sm.add_widget(SongScreen())
            sm.current = screen_name

class AlbumArtLeftWidget(ILeftBody, FitImage):
    pass

class SongItem(TwoLineAvatarIconListItem):
    song_id = NumericProperty()
    artwork = None

class SongListScreen(MDBottomNavigationItem):

    def convert_seconds_to_min(self, sec):
        val = str(datetime.timedelta(seconds = sec)).split(':')
        return f'{val[1]}:{val[2].split(".")[0]}'

    def __init__(self, *args, **kwargs):
        super(SongListScreen, self).__init__(*args, **kwargs)
        self.all_songs = MDApp.get_running_app().all_songs
        # Window.bind(on_resize=self.window_size_changed)
        # print(Metrics.dpi)

        Clock.schedule_once(self.populate_song_list)

    def populate_song_list(self, *args):
        for id in self.all_songs.keys():
            song = self.all_songs[id]
            item = SongItem(
                text= song['name'],
                secondary_text=f"[size=12]{song['artist']}[/size]",
                on_release= self.play_song if platform == 'android' else lambda x: print(''),
            )
            item.song_id = id
            item.ids.artwork_thumb.texture = item.artwork = song['artwork']
            item.ids.audio_length.text = self.convert_seconds_to_min(song['length'])
            self.ids.songs_list.add_widget(item)

    def play_song(self, *args):
        app = MDApp.get_running_app()
        app.now_playing = self.all_songs[args[0].song_id]

        sm = app.sm
        screen_name = 'song_screen'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            from screens.song import SongScreen
            sm.add_widget(SongScreen())
            sm.current = screen_name
