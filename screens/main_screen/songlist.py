from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBody, IRightBody, IRightBodyTouch
from kivymd.utils.fitimage import FitImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard

from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.metrics import Metrics
from kivy.utils import platform
from kivy.uix.recycleview import RecycleView

import datetime
from libs.database.get import song

Builder.load_string('''
<SongListItem>:
    text: self.name
    secondary_text: self.artist
    font_style: 'OpenSans'
    divider: 'Full'
    # on_size:
    #     self.ids._right_container.width = right_widgets.width
    #     self.ids._right_container.x = right_widgets.width
    AlbumArtLeftWidget:
        id: artwork_thumb
        texture: root.image

    RightWidgets:
        id: right_widgets
        size_hint_x: 1

        MDLabel:
            id: audio_length
            text: root.length
            font_style: 'OpenSans'
            theme_text_color: 'Secondary'

<SongCardItem>:
    spacing: dp(5)
    FitImage:
        texture: root.image
        size_hint_x: 0.25
    MDLabel:
        text: root.name
        font_style: 'OpenSans'
    MDLabel:
        text: root.artist
        font_style: 'OpenSans'
    MDLabel:
        text: root.length
        font_style: 'OpenSans'
    MDIconButton:
        icon: 'play'
        on_release: root.toggle_song(root.id)


<SongListScreen>:
    RecycleView:
        id: song_list_rv
        # viewclass: 'SongListItem'
        viewclass: 'SongCardItem'
        RecycleGridLayout:
            default_size: None, dp(56)
            cols: 1
            spacing: dp(5)
            padding: [dp(10), dp(10)]
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
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

class SongListItem(TwoLineAvatarIconListItem):
    id = NumericProperty()
    name = StringProperty()
    artist = StringProperty()
    image = ObjectProperty()
    length = StringProperty()

class SongCardItem(MDCard):
    id = NumericProperty()
    name = StringProperty()
    artist = StringProperty()
    image = ObjectProperty()
    length = StringProperty()

    def __init__(self, *args, **kwargs):
        super(SongCardItem, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def toggle_song(self, song_id, *args):
        self.app.now_playing = song(song_id)

        sm = self.app.sm
        screen_name = 'song_screen'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            from screens.song import SongScreen
            sm.add_widget(SongScreen())
            sm.current = screen_name

class SongListScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(SongListScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.app.bind(all_songs=self.populate_song_list)

    def populate_song_list(self, *args):
        self.ids.song_list_rv.data = self.app.all_songs

    # def play_song(self, *args):
    #     app = MDApp.get_running_app()
    #     app.now_playing = self.all_songs[args[0].song_id]
    #
    #     sm = app.sm
    #     screen_name = 'song_screen'
    #     if sm.has_screen(screen_name):
    #         sm.current = screen_name
    #     else:
    #         from screens.song import SongScreen
    #         sm.add_widget(SongScreen())
    #         sm.current = screen_name
