import os
os.environ['KIVY_AUDIO'] = "ffpyplayer"
# import ffpyplayer.player.core

from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineAvatarListItem, TwoLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.picker import MDThemePicker
# from kivymd.utils.fitimage import FitImage

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, DictProperty, NumericProperty, StringProperty, BooleanProperty, ObjectProperty, OptionProperty
from kivy.clock import Clock
from kivy.core.audio import Sound, SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy import platform

from plyer import storagepath
if platform == 'android':
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    from kivmob import KivMob, TestIds

import glob
import pathlib
import datetime
import mutagen
import json
import socket
import time
from functools import partial

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

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


class SettingsThemeScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(SettingsThemeScreen, self).__init__(*args, *kwargs)
        self.app = MDApp.get_running_app()
        self.theme_cls = self.app.theme_cls
        self.config = self.app.config

        self.theme_cls.bind(theme_style=partial(self.theme_changed, 'theme_style'),
                            primary_palette=partial(self.theme_changed, 'primary_palette'),
                            accent_palette=partial(self.theme_changed, 'accent_palette'))

    def theme_changed(self, *args, **kwargs):
        self.config.set('theme', args[0], args[2])
        self.config.write()

    def open_theme_picker(self, *args):
        theme_picker = MDThemePicker()
        theme_picker.open()


class SettingsNowPlayingScreen(Screen):
    dialog = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(SettingsNowPlayingScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.config = self.app.config

    def set_now_playing_background(self, bg, *args):
        # print(args)
        if self.collide_point(*args[1].pos):
            # print(bg)
            self.app.now_playing_background = bg
            self.config.set('now-playing', 'background', bg)
            self.config.write()

    def open_background_selector(self, *args):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Choose background",
                type="simple",
                items=[
                    TwoLineListItem(text="Default", secondary_text="the default theme background", on_touch_down=partial(self.set_now_playing_background, 'default')),
                    TwoLineListItem(text="Artwork Color", secondary_text="the dominant color from artwork", on_touch_down=partial(self.set_now_playing_background, 'artwork-color')),
                    TwoLineListItem()
                ],
            )
        self.dialog.open()


class SettingsScreen(Screen):
    dialog = None

    def __init__(self, *args, **kwargs):
        super(SettingsScreen, self).__init__(*args, **kwargs)
        self.sm = MDApp.get_running_app().sm

    def go_to_main(self, *args):
        MDApp.get_running_app().sm.current = 'main_screen'

    def go_to_themes(self, *args):
        screen_name = 'theme_settings'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            self.sm.add_widget(SettingsThemeScreen())

    def go_to_now_playing(self, *args):
        screen_name = 'now_playing_settings'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            self.sm.add_widget(SettingsNowPlayingScreen())

    def go_to_search_paths(self, *args):
        screen_name = 'settings_search_paths'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            self.sm.add_widget(SettingsSearchPathsScreen())



class HomeScreen(MDBottomNavigationItem):
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            self.app.ads.show_interstitial()
        self.app.client.send_message(b'/print_api', ['in home_screen'.encode('utf8'), ])

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


SERVICE_NAME = u'com.matrix.music_player.ServiceMatrix'

def print_api(message, *args):
    print("Message from service : ", message)

class MainApp(MDApp):
    all_songs = DictProperty()
    now_playing = DictProperty()

    now_playing_background = OptionProperty('default', options=['default', 'artwork-color'])

    remote_id = StringProperty('')
    remote_songs = DictProperty()
    remote_client = None

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
        self.service = None
        # ANDROID SPECIFIC SETUPS
        if platform == 'android':
            # ADS
            self.ads = KivMob('ca-app-pub-9614085129932704~9292191302')
            # self.ads = KivMob(TestIds.APP)
            self.ads.new_interstitial('ca-app-pub-9614085129932704/7878488547')
            # self.ads.new_interstitial(TestIds.INTERSTITIAL)
            self.ads.request_interstitial()
            # SERVICE
            self.service = autoclass(SERVICE_NAME)
            mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            self.service.start(mActivity, argument)

        # SERVER - CLIENT IMPLEMENATION
        self.server = OSCThreadServer()
        self.server.listen(address='0.0.0.0', port=3002, default=True)
        self.server.bind(b'/print_api', print_api)
        self.server.bind(b'/set_remote_id', self.set_remote_id)
        self.server.bind(b'/send_all_songs', self.send_all_songs)
        self.server.bind(b'/set_remote_songs', self.set_remote_songs)
        self.server.bind(b'/send_song', self.send_song)
        self.server.bind(b'/recieve_song', self.recieve_song)

        self.client = OSCClient('0.0.0.0', 3000)

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

    def send_all_songs(self, *args):
        all_songs_new = self.all_songs
        for id in all_songs_new.keys():
            if 'artwork' in all_songs_new[id]: del all_songs_new[id]['artwork']

        self.remote_client.send_message(b'/set_remote_songs', [json.dumps(all_songs_new).encode('utf8'), ])

    def set_remote_id(self, message, *args):
        self.remote_id = message.decode('utf8')

    def set_remote_songs(self, message, *args):
        remote_songs = message.decode('utf8')
        self.remote_songs = json.loads(remote_songs)

    def send_song(self, message, *args):
        song_id = message.decode('utf8')
        song_info = self.all_songs[int(song_id)]
        song_path = song_info['path']
        song_name = song_info['name']
        self.remote_client.send_message(b'/recieve_song', [song_name.encode('utf8')])
        time.sleep(1) # wait for reciever to initialize
        port = 5001
        buffer_size = 1024
        filesize = os.path.getsize(song_path)

        s = socket.socket()
        s.connect((self.remote_id, port))

        with open(song_path, "rb") as f:
            packet = f.read(buffer_size)
            while len(packet) != 0:
                s.send(packet)
                packet = f.read(buffer_size)

        s.close()

    def recieve_song(self, message, *args):
        song_name = message.decode('utf8')
        print(song_name)
        buffer_size = 1024

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 5001))
        s.listen(5)
        client_socket, address = s.accept()

        with open(f"remote_temp/{song_name}.mp3", "wb") as f:
            packet = client_socket.recv(buffer_size)
            while len(packet) != 0:
                f.write(packet)
                packet = client_socket.recv(buffer_size)

        s.close()

        song_path = f'remote_temp/{song_name}.mp3'

        self.all_songs[999] = {
            'id': 999,
            'path': song_path,
            'name': song_name,
            'artwork': self.extract_song_artwork(song_path, 999)
        }
        self.now_playing = self.all_songs[999]

        screen_name = 'song_screen'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            self.sm.add_widget(SongScreen())
            self.sm.current = screen_name

    def on_remote_id(self, instance, value):
        self.remote_client = OSCClient(value, 3002)

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
        config.setdefaults('theme', {
            'theme_style': 'Light',
            'primary_palette': 'Blue',
            'accent_palette': 'Amber'
        })
        config.setdefaults('now-playing', {
            'background': 'default'
        })

    def keyboard_handler(self, window, key, scancode=None, codepoint=None, modifier=None, **kwargs):
        if key == 27:
            if self.sm.current == 'main_screen':
                return False
            self.sm.current = self.sm.previous()
            return True

    def on_start(self):
        # ADS
        # if platform == 'android':
        #     self.ads.show_interstitial()

        # Redefine KivyMD's Dark Color Palette to match Material Design Spec
        from kivymd.color_definitions import colors
        colors["Dark"] = {
            "StatusBar": "000000",
            "AppBar": "1f1f1f",
            "Background": "121212",
            "CardsDialogs": "1d1d1d",
            "FlatButtonDown": "999999",
        }

        # APPLY THEMING HERE FOR NOW
        config = self.config
        self.theme_cls.theme_style = config.get('theme', 'theme_style')
        self.theme_cls.primary_palette = config.get('theme', 'primary_palette')
        self.theme_cls.accent_palette = config.get('theme', 'accent_palette')

        self.now_playing_background = config.get('now-playing', 'background')

        Window.bind(on_keyboard=self.keyboard_handler)

    def on_stop(self):
        if self.service:
            self.service.stop()
        else:
            pass

    def on_pause(self):
        return True

    def on_resume(self):
        if platform == 'android':
            self.ads.request_interstitial()



if __name__ == '__main__':
    MainApp().run()
