from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.card import MDCard

from kivy.utils import platform
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

from plyer import storagepath
if platform == 'android':
    from android.permissions import request_permissions, Permission

from libs.database.get import all_artists, most_listened_songs, song

Builder.load_string('''
#:import ArtistCard screens.main_screen.artists.ArtistCard

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        MDLabel:
            text: 'Artists'
            theme_text_color: "Secondary"
            size_hint_y: None
            size: self.texture_size
            halign: 'center'
            font_style: "Button"
        RecycleView:
            id: top_artists_rv
            viewclass: 'ArtistCard'
            size_hint_y: 0.3
            do_scroll_x: True
            do_scroll_y: False
            RecycleBoxLayout:
                orientation: 'horizontal'
                padding: [10, 10, 10, 10]
                default_size_hint: None, 1
                default_size: self.height, None
                size_hint_x: None
                width: self.minimum_width
        # MDLabel:
        #     text: "WILL BE POPULATED SOON"
        #     theme_text_color: "Hint"
        #     font_style: "OpenSans"
        #     halign: 'center'
        #     position: {'center_x': 0.5, 'center_y': '0.5'}

        BoxLayout:
            orientation: 'horizontal'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.5
                MDLabel:
                    text: 'Top Tracks'
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    size: self.texture_size
                    halign: 'center'
                    font_style: "Button"
                RecycleView:
                    id: top_songs_rv
                    viewclass: 'TopSongsCard'
                    do_scroll_x: False
                    do_scroll_y: True
                    RecycleGridLayout:
                        # orientation: 'vertical'
                        cols: 2
                        padding: [10, 10, 10, 10]
                        spacing: dp(20)
                        default_size_hint: 1, None
                        default_size: None, dp(72)
                        size_hint_y: None
                        height: self.minimum_height
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.5

        # MDFlatButton:
        #     text: "LOAD AMAZON AD"
        #     on_release: root._load_ad('amazon')
        #
        # MDFlatButton:
        #     text: "LOAD ADMOB AD"
        #     on_release: root._load_ad('admob')

<TopSongsCard>:
    spacing: dp(5)
    focus_behaviour: True
    ripple_behaviour: True
    on_touch_up: if self.collide_point(*args[1].pos): root.toggle_song(root.id)
    FitImage:
        texture: root.image
        size_hint_x: None
        width: self.height
    BoxLayout:
        orientation: 'vertical'
        padding: [10, 0, 0, 0]
        MDLabel:
            text: root.name
            font_style: 'OpenSans'
            theme_text_color: 'Primary'
        MDLabel:
            text: root.artist
            font_style: 'OpenSans'
            theme_text_color: 'Secondary'
    # MDIconButton:
    #     icon: 'play'
    #     on_release: root.toggle_song(root.id)
''')

class TopSongsCard(MDCard):
    id = NumericProperty()
    name = StringProperty()
    artist = StringProperty()
    image = ObjectProperty()
    length = StringProperty()

    def __init__(self, *args, **kwargs):
        super(TopSongsCard, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def toggle_song(self, song_id, *args):
        try:
            if song_id != self.app.now_playing['id']:
                self.app.now_playing = song(song_id)
        except:
            self.app.now_playing = song(song_id)

        sm = self.app.sm
        screen_name = 'song_screen'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            from screens.song import SongScreen
            sm.add_widget(SongScreen())
            sm.current = screen_name



class HomeScreen(MDBottomNavigationItem):
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        Clock.schedule_once(self.update_widgets)

        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        try:
            self.app.client.send_message(b'/print_api', ['in home_screen'.encode('utf8'), ])
        except Exception as e:
            print(e)

    def update_widgets(self, *args):
        self.ids.top_artists_rv.data = all_artists()
        self.ids.top_songs_rv.data = most_listened_songs()

    def _load_ad(self, source, *args):
        if source == 'admob':
            self.app.ads.show_interstitial()
        else:
            self.app.InterstitialAd.showAd()
