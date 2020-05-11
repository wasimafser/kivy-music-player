import os
os.environ['KIVY_AUDIO'] = "ffpyplayer"
# import ffpyplayer.player.core

from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineAvatarListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.behaviors import RectangularElevationBehavior
# from kivymd.utils.fitimage import FitImage

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, DictProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.audio import Sound, SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy import platform

from plyer import storagepath
if platform == 'android':
    from android.permissions import request_permissions, Permission

import glob
import pathlib
import datetime
import mutagen

# Window.borderless = True

class MainScreen(Screen):
    """
    Main Screen for the app
    """
    def go_to_settings(self, *args):
        sm = MDApp.get_running_app().sm
        screen_name = 'settings_screen'
        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            sm.add_widget(SettingsScreen(name=screen_name))

class ItemWithRemove(OneLineAvatarIconListItem):
    pass

class SettingsSearchPathsScreen(Screen):
    search_path_items = ListProperty()

    def __init__(self, *args, **kwargs):
        super(SettingsSearchPathsScreen, self).__init__(*args, **kwargs)
        self.config = MDApp.get_running_app().config
        self.search_paths = str(self.config.get('search-paths', 'folders')).split(',')

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
            # previous=True,
        )
        default_path = '/'
        if platform == 'android':
            default_path = '/storage/emulated/0'
        self.file_manager.show(default_path)

    def select_path(self, path):
        self.exit_manager()
        self.search_paths.append(path)
        all_paths = ','.join(self.search_paths)
        self.config.set('search-paths', 'folders', all_paths)
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
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class SongItem(OneLineAvatarListItem):
    song_id = NumericProperty()
    artwork = None
    pass

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
        self.play_song()

    def play_song(self, *args):
        now_playing = self.app.now_playing
        self.song_path = now_playing['path']
        self.song_name = now_playing['name']

        self.ids.album_art.texture = now_playing['artwork']
        Clock.schedule_once(self.compute_average_image_color, 0.5)
        if self.song is not None:
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
        folders = str(config.get('search-paths', 'folders')).split(',')
        id = 0
        for folder in folders:
            for format in ['mp3', 'wav']:
                for file in glob.glob(f"{folder}/*.{format}"):
                    self.all_songs[id] = {
                        'id': id,
                        'path': file,
                        'name': pathlib.Path(file).stem,
                        'artwork': self.extract_song_artwork(file, id)
                    }
                    id += 1

        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main_screen'))
        return self.sm

    def build_config(self, config):
        default_path = '/'
        if platform == 'android':
            # default_path = storagepath.get_music_dir()
            default_path = '/storage/emulated/0/Music'
        config.setdefaults('search-paths', {
            'folders': default_path
        })
        config.setdefaults('graphics', {
            'borderless': '1'
        })

    def keyboard_handler(self, window, key, scancode=None, codepoint=None, modifier=None, **kwargs):
        if key == 27:
            if self.sm.current == 'main_screen':
                return False
            self.sm.current = self.sm.previous()
            return True

    def on_start(self):
        Window.bind(on_keyboard=self.keyboard_handler)

    def on_stop(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass



if __name__ == '__main__':
    MainApp().run()
