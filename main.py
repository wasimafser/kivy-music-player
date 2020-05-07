import os
os.environ['KIVY_AUDIO'] = "ffpyplayer"

from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineAvatarListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.behaviors import RectangularElevationBehavior

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, DictProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle

import glob
import pathlib
import datetime
import mutagen

class MainScreen(Screen):
    """
    Main Screen for the app
    """
    def go_to_settings(self, *args):
        MDApp.get_running_app().sm.current = 'settings_screen'

class ItemWithRemove(OneLineAvatarIconListItem):
    pass

class SettingsSearchPathsScreen(Screen):
    search_path_items = ListProperty()

    def __init__(self, *args, **kwargs):
        super(SettingsSearchPathsScreen, self).__init__(*args, **kwargs)
        self.config = MDApp.get_running_app().config
        self.search_paths = str(self.config.get('search_paths', 'folders')).split(',')

        for path in self.search_paths:
            item = ItemWithRemove(
                text = path
            )
            self.search_path_items.append(item)

        Clock.schedule_once(self.populate_list)

    def populate_list(self, *args):
        for item in self.search_path_items:
            self.ids.search_paths_list.add_widget(item)

    def go_to_settings(self, *args):
        MDApp.get_running_app().sm.current = 'settings_screen'

    def launch_file_manager(self, *args):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            previous=True,
        )
        self.file_manager.show('/')

    def select_path(self, path):
        self.exit_manager()
        self.search_paths.append(path)
        all_paths = ','.join(self.search_paths)
        self.config.set('search_paths', 'folders', all_paths)
        self.config.write()

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()


class SettingsScreen(Screen):
    dialog = None

    def go_to_main(self, *args):
        MDApp.get_running_app().sm.current = 'main_screen'

    def go_to_search_paths(self, *args):
        sm = MDApp.get_running_app().sm
        screen_name = 'settings_search_paths'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            sm.add_widget(SettingsSearchPathsScreen())


class HomeScreen(MDBottomNavigationItem):
    pass

class SongItem(OneLineAvatarListItem):
    song_id = NumericProperty()
    artwork = None

class NowPlayingAlbumArt(Image, RectangularElevationBehavior):
    pass

class SongScreen(Screen):
    song_max_length = NumericProperty(0)
    song_current_pos = NumericProperty(0)
    song_path = StringProperty('')
    avg_artwork_color = (0, 0, 0)
    song = None
    song_state = StringProperty('pause')
    song_name = StringProperty('')

    def convert_seconds_to_min(self, sec):
        val = str(datetime.timedelta(seconds = sec)).split(':')
        return f'{val[1]}:{val[2].split(".")[0]}'

    def go_to_main(self, *args):
        MDApp.get_running_app().sm.current = 'main_screen'

    def compute_average_image_color(self, *args):
        img = self.ids.album_art.texture
        width, height = img.size

        r_total = 0
        g_total = 0
        b_total = 0

        count = 0
        for x in range(0, width):
            for y in range(0, height):
                p = img.get_region(x,y, x+1, y+1).pixels
                r, g, b, a = p[0], p[1], p[2], p[3]
                # r, g, b, a = img.get_region(x,y, x+1, y+1).pixels
                r_total += r
                g_total += g
                b_total += b
                count += 1

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
        self.play_song()

    def play_song(self, *args):
        now_playing = self.app.now_playing
        self.song_path = now_playing['path']
        self.song_name = now_playing['name']
        
        self.ids.album_art.texture = now_playing['artwork']
        # Clock.schedule_once(self.compute_average_image_color, 0.5)
        if self.song is not None:
            self.song.stop()
            self.song.unload()

        self.song = SoundLoader.load(self.song_path)
        if self.song:
            self.song_max_length = self.song.length
            self.ids.song_total_length_label.text = self.convert_seconds_to_min(self.song_max_length)
            self.song.play()
            Clock.schedule_interval(self.manage_song, 1)

    def manage_song(self, *args):
        # print(self.song.get_pos(), self.song.length)
        self.song_current_pos = self.song.get_pos()
        self.ids.song_cur_pos_label.text = self.convert_seconds_to_min(self.song_current_pos)

    def seek_song(self, *args):
        print("touched")
        self.song_current_pos = self.ids.song_slider.value
        self.song.seek(self.song_current_pos)

    def toggle_song_play(self, *args):
        if self.song.state == 'play':
            self.song_state = 'play'
            self.song.stop()
        elif self.song.state == 'stop':
            self.song_state = 'pause'
            self.song.play()

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
            sm.add_widget(SongScreen())
            sm.current = screen_name



class MainApp(MDApp):
    all_songs = DictProperty()
    now_playing = DictProperty()

    def extract_song_artwork(self, song_path, song_id):
        import io
        try:
            song_file = mutagen.File(song_path)
            artwork_data = song_file.tags['APIC:'].data
            artwork = CoreImage(io.BytesIO(artwork_data), ext='png', filename=f"{song_id}.png", mipmap=True).texture
        except Exception as e:
            print("has error")
            artwork_data = io.BytesIO(open('artwork/default.jpg', 'rb').read())
            artwork = CoreImage(artwork_data, ext='png', mipmap=True).texture

        return artwork

    def build(self):
        # SEARCH FOR SONGS FROM THE GIVEN PATHS
        config = self.config
        folders = str(config.get('search_paths', 'folders')).split(',')
        id = 0
        for folder in folders:
            for format in ['mp3', 'wav']:
                for file in glob.glob(f"{folder}/*.{format}"):
                    self.all_songs[id] = {
                        'path': file,
                        'name': pathlib.Path(file).stem,
                        'artwork': self.extract_song_artwork(file, id)
                    }
                    id += 1

        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main_screen'))
        self.sm.add_widget(SettingsScreen(name='settings_screen'))
        return self.sm

    def build_config(self, config):
        config.setdefaults('APP', {
            'version': '1'
        })

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass



if __name__ == '__main__':
    MainApp().run()
