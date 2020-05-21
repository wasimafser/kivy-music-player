from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.list import OneLineAvatarListItem

from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.lang.builder import Builder


Builder.load_string('''
<SongItem>:
    ImageLeftWidget:
        id: artwork_thumb
        allow_stretch: True
        keep_ratio: False
        size_hint: 1, 1

<SongListScreen>:
    BoxLayout:
        orientation: "vertical"

        ScrollView:
            MDList:
                id: songs_list
''')


class SongItem(OneLineAvatarListItem):
    song_id = NumericProperty()
    artwork = None
    pass

class SongListScreen(MDBottomNavigationItem):

    def __init__(self, *args, **kwargs):
        super(SongListScreen, self).__init__(*args, **kwargs)
        self.all_songs = MDApp.get_running_app().all_songs

        Clock.schedule_once(self.populate_song_list)

    def populate_song_list(self, *args):
        for id in self.all_songs.keys():
            song = self.all_songs[id]
            item = SongItem(
                text= song['name'],
                on_release= self.play_song,
            )
            item.song_id = id
            item.ids.artwork_thumb.texture = item.artwork = song['artwork']
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
