from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDIconButton
from kivymd.utils.fitimage import FitImage

from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty, DictProperty, NumericProperty, StringProperty
from kivy.clock import Clock

from libs.database.get import all_artists, artist, artist_songs, song

Builder.load_string('''
<ArtistsScreen>:
    RecycleView:
        id: artists_rv
        viewclass: 'ArtistCard'
        # size_hint_y: 0.3
        do_scroll_x: False
        do_scroll_y: True
        RecycleGridLayout:
            # orientation: 'vertical'
            cols: 3
            padding: [10, 10, 10, 10]
            # default_size_hint: None, 1
            default_size_hint: 1, None
            # default_size: self.height, None
            default_size: None, dp(250)
            # size_hint_x: None
            size_hint_y: None
            # width: self.minimum_width
            height: self.minimum_height
            # canvas.before:
            #     Color:
            #         rgba: (1, 0, 0, 1)
            #     Rectangle:
            #         size: self.size
            #         pos: self.pos


<ArtistCard>:
    orientation: 'vertical'
    on_touch_up: if self.collide_point(*args[1].pos): self.show_artist_songs(self.id)
    MDCard:
        size_hint_x: None
        pos_hint: {'center_x': 0.5}
        width: self.height
        FitImage:
            texture: root.image
    MDLabel:
        text: root.name
        halign: 'center'
        size_hint_y: 0.15
        font_style: 'OpenSans'
        theme_text_color: 'Primary'

<ArtistSongsDialogContent>:
    BoxLayout:
        pos_hint: {'center_y': 0.5, 'center_x': 0.5}
        orientation: 'horizontal'
        MDCard:
            FitImage:
                id: artist_songs_img
        RecycleView:
            id: aritst_songs_rv
            viewclass: 'ArtistSongsCard'
            do_scroll_x: False
            do_scroll_y: True
            RecycleBoxLayout:
                orientation: 'vertical'
                padding: [10, 10, 10, 10]
                spacing: dp(20)
                default_size_hint: 1, None
                default_size: None, dp(72)
                size_hint_y: None
                height: self.minimum_height


<ArtistSongsCard>:
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
            valign: 'center'
            theme_text_color: 'Primary'
    # MDIconButton:
    #     icon: 'play'
    #     on_release: root.toggle_song(root.id)
''')

class ArtistSongsCard(MDCard):
    id = NumericProperty()
    name = StringProperty()
    artist = StringProperty()
    image = ObjectProperty()
    length = StringProperty()

    def __init__(self, *args, **kwargs):
        super(ArtistSongsCard, self).__init__(*args, **kwargs)
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

class ArtistSongsDialogContent(FloatLayout):
    dialog = None
    artist_id = NumericProperty()
    artist_data = DictProperty()

    def __init__(self, *args, **kwargs):
        super(ArtistSongsDialogContent, self).__init__(*args, **kwargs)
        self.artist_data = artist(self.artist_id)

        Clock.schedule_once(self.update_widgets)

    def update_widgets(self, *args):
        self.ids.artist_songs_img.texture = self.artist_data['image']
        self.ids.aritst_songs_rv.data = artist_songs(self.artist_id)

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()


class ArtistCard(BoxLayout):
    id = NumericProperty()
    image = ObjectProperty()
    name = StringProperty()

    dialog = None

    def __init__(self, *args, **kwargs):
        super(ArtistCard, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def show_artist_songs(self, id, *args):
        if not self.dialog:
            self.dialog = ModalView(size_hint=(0.9, 0.9), background_color=self.app.theme_cls.bg_light)
            content = ArtistSongsDialogContent(artist_id=id)
            content.add_widget(MDIconButton(icon='close', pos_hint={'top': 1, 'right': 1}, on_release=lambda x: self.dialog.dismiss()))
            self.dialog.add_widget(content)
        self.dialog.open()

class ArtistsScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(ArtistsScreen, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.set_artists_data)

    def set_artists_data(self, *args):
        self.ids.artists_rv.data = all_artists()
