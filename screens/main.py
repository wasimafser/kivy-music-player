from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.utils.fitimage import FitImage

from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, DictProperty, NumericProperty, StringProperty
from kivy.clock import Clock

import datetime

Builder.load_string('''
#:import HomeScreen screens.main_screen.home.HomeScreen
#:import SongListScreen screens.main_screen.songlist.SongListScreen
#:import ArtistsScreen screens.main_screen.artists.ArtistsScreen
#:import SPlayScreen screens.main_screen.splay.SPlayScreen

<MainScreen>:
    id: main_screen
    FloatLayout:
        id: main_layout

        BoxLayout:
            id: top_bar
            size_hint: 0.9, 0.05
            pos_hint: {'center_x': 0.5, 'top': 1}

            # StackLayout:
            BoxLayout:
                id: top_bar_box
                # orientation: 'lr-tb'
                orientation: 'horizontal'

                MDIconButton:
                    id: menu_btn
                    icon: 'menu'
                    on_release: nav_drawer.toggle_nav_drawer()

                TextInput:
                    multiline: False
                    padding: [0, (self.height-self.line_height)/2]
                    background_normal: 'assets/transparent.png'
                    background_active: 'assets/transparent.png'
                    hint_text: 'Search'

                MDIconButton:
                    id: settings_btn
                    icon: 'settings'
                    pos_hint: {'right': 1}
                    on_release: root.go_to_settings()

        NavigationLayout:
            id: nav_layout
            pos_hint: {'right': 1}
            # canvas.before:
            #     Color:
            #         rgba: (1, 0, 0, 1)
            #     Rectangle:
            #         size: self.size
            #         pos: self.pos

            ScreenManager:
                size_hint_y: 0.95
                id: sm
                pos_hint: {'right': 1}

                HomeScreen:
                    name: "home_screen"

                SongListScreen:
                    name: "song_list_screen"

                ArtistsScreen:
                    name: 'artists_screen'


            MDNavigationDrawer:
                id: nav_drawer
                orientation: 'vertical'
                on_state:
                    # menu_btn.opacity = 1 if self.state == 'close' else 0
                    menu_btn.opacity = 1 if self.state == 'close' else 0

                BoxLayout:
                    id: app_logo
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: avatar.height

                    Image:
                        id: avatar
                        size_hint: None, None
                        size: "56dp", "56dp"
                        source: "assets/icon.png"

                    MDLabel:
                        text: 'MATRIX MUSIC PLAYER'
                        font_style: 'OpenSans'
                        halign: 'center'
                        valign: 'center'
                        theme_text_color: 'Primary'

                ScrollView:
                    id: nav_items
                    MDList:
                        OneLineListItem:
                            text: 'YOUR LIBRARY'
                            font_style: 'OpenSans'
                        OneLineIconListItem:
                            text: 'Home'
                            divider: None
                            on_release: sm.current = 'home_screen'

                            IconLeftWidget:
                                icon: 'home'

                        OneLineIconListItem:
                            text: 'Songs'
                            divider: None
                            on_release: sm.current = 'song_list_screen'

                            IconLeftWidget:
                                icon: 'music'

                        OneLineIconListItem:
                            text: 'Artists'
                            divider: None
                            on_release: sm.current = 'artists_screen'

                            IconLeftWidget:
                                icon: 'account'

<MiniPlayer>:
    size_hint: 0.9, 0.1
    pos_hint: {'center_x': 0.5, 'top': 0.12}
    on_release:
        app.sm.current = 'song_screen'
    BoxLayout:
        id: image_box
        size_hint_x: None
        width: self.height
    BoxLayout:
        orientation: 'horizontal'
        canvas.before:
            Color:
                rgba: app.theme_cls.bg_dark
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.8
            BoxLayout:
                orientation: 'horizontal'
                padding: [20, 10, 0, 0]
                spacing: dp(5)
                # canvas.before:
                #     Color:
                #         rgba: (1, 0,0, 1)
                #     Rectangle:
                #         pos: self.pos
                #         size: self.size
                MDLabel:
                    id: mini_song_name
                    text: root.song_name
                    # font_size: '20sp'
                    halign: 'left'
                    font_style: 'OpenSans'
                    theme_text_color: 'Primary'
                MDLabel:
                    text: root.artist_name
                    halign: 'left'
                    font_style: 'OpenSans'
                    theme_text_color: 'Secondary'
            # MDLabel:
            #     id: mini_current_pos
            #     size_hint_x: None
            #     halign: 'right'
            #     font_style: 'OpenSans'
            #     theme_text_color: 'Primary'
            # MDLabel:
            #     id: mini_total_length
            #     size_hint_x: None
            #     halign: 'right'
            #     font_style: 'OpenSans'
            #     theme_text_color: 'Primary'
            MDSlider:
                id: mini_seeker
                min: 0
                max: root.song_max_length
                value: root.song_current_pos
                hint: False
                on_touch_up: if self.collide_point(*args[1].pos): root.seek_song(self.value)
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            size_hint: 0.2, 1
            BoxLayout:
                orientation: 'horizontal'
                size_hint: None, None
                height: self.minimum_height
                width: self.minimum_width
                MDIconButton:
                    icon: 'skip-previous'
                    on_release: root.main_song_screen.prev_song()
                MDIconButton:
                    icon: root.song_state
                    on_release: root.main_song_screen.toggle_song_play()
                MDIconButton:
                    icon: 'skip-next'
                    on_release: root.main_song_screen.next_song()
''')

class MiniPlayer(MDCard):
    data = DictProperty()
    mini_artwork = ObjectProperty()

    song_max_length = NumericProperty(0)
    song_current_pos = NumericProperty(0)
    song_name = StringProperty()
    artist_name = StringProperty()
    song_state = StringProperty('pause')

    main_song_screen = ObjectProperty()

    def convert_seconds_to_min(self, sec):
        val = str(datetime.timedelta(seconds = sec)).split(':')
        return f'{val[1]}:{val[2].split(".")[0]}'

    def __init__(self, *args, **kwargs):
        super(MiniPlayer, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        Clock.schedule_once(self.get_song_screen)

        self.mini_artwork = FitImage(texture=self.data['image'])
        self.ids.image_box.add_widget(self.mini_artwork)
        # self.bind(data=self.update_info)

    def get_song_screen(self, *args):
        for screen in self.app.sm.screens:
            if screen.name == 'song_screen':
                self.main_song_screen = screen

        self.main_song_screen.bind(song_current_pos=self.update_current_pos)
        self.main_song_screen.bind(song_state=self.set_state)
        self.main_song_screen.bind(song=self.update_info)
        self.update_info(None, self.main_song_screen.song)

    def set_state(self, instance, value):
        self.song_state=value

    def update_current_pos(self, instance, value):
        self.song_current_pos = value
        # self.ids.mini_current_pos.text = f"{self.convert_seconds_to_min(value)}"

    def seek_song(self, *args):
        self.main_song_screen.seek_song(args[0])

    def update_info(self, instance, value):
        self.song_max_length = value.length
        # self.ids.mini_total_length.text = self.convert_seconds_to_min(self.song_max_length)
        self.song_name = self.data['name']
        self.artist_name = self.data['artist']
        self.mini_artwork.texture = self.data['image']

class MainScreen(Screen):
    """
    Main Screen for the app
    """
    mini_player = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(MainScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.app.bind(now_playing=self.update_mini_player)

    def update_mini_player(self, *args):
        if not self.mini_player:
            self.mini_player = MiniPlayer(data=self.app.now_playing)
            self.add_widget(self.mini_player)
        else:
            self.mini_player.data = self.app.now_playing

    def go_to_settings(self, *args):
        sm = self.app.sm
        screen_name = 'settings_screen'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            from screens.settings import SettingsScreen
            sm.add_widget(SettingsScreen(name=screen_name))
