import os
os.environ['KIVY_AUDIO'] = "ffpyplayer"

from kivymd.app import MDApp
from kivymd.uix.card import MDCard

from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, DictProperty, NumericProperty, StringProperty, BooleanProperty, ObjectProperty, OptionProperty
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp

from plyer import storagepath
if platform == 'android':
    from jnius import autoclass, cast

import pathlib
import datetime
import mutagen
import json
import socket
import time
import io
from functools import partial

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

from libs.database import db_main, get

SERVICE_NAME = u'matrix.music_player.ServiceMatrix'

def print_api(message, *args):
    print("Message from service : ", message)

class MainApp(MDApp):
    # all_songs = DictProperty()
    all_songs = ListProperty()
    now_playing = DictProperty()

    now_playing_background = OptionProperty('default', options=['default', 'artwork-color'])

    remote_id = StringProperty('')
    remote_songs = DictProperty()
    remote_client = None

    def extract_song_artwork(self, song_path, song_id, *args):
        try:
            song_file = mutagen.File(song_path)
            if song_path.suffix == '.mp3':
                artwork_data = song_file.tags['APIC:'].data
                artwork = CoreImage(io.BytesIO(artwork_data), ext='png', filename=f"{song_id}.png", mipmap=True).texture
            elif song_path.suffix == '.m4a':
                artwork_data = song_file.tags['covr'][0]
                artwork = CoreImage(io.BytesIO(artwork_data), ext='png', filename=f"{song_id}.png", mipmap=True).texture
            else:
                artwork_data = io.BytesIO(open('artwork/default.jpg', 'rb').read())
                artwork = CoreImage(artwork_data, ext='png', mipmap=True).texture
        except Exception as e:
            # print("has error", e)
            artwork_data = io.BytesIO(open('artwork/default.jpg', 'rb').read())
            artwork = CoreImage(artwork_data, ext='png', mipmap=True).texture

        if song_id == 'remote':
            self.all_songs[song_id]['artwork'] = artwork
            return

        return artwork

    def build(self):
        self.service = None
        # ANDROID SPECIFIC SETUPS
        if platform == 'android':
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            currentActivity = cast('android.app.Activity', mActivity)
            context = cast('android.content.Context', currentActivity.getApplicationContext())

            # ADMOB ADS
            # AdColonyAppOptions = autoclass("com.adcolony.sdk.AdColonyAppOptions")
            # appOptions = AdColonyAppOptions()
            # appOptions.setGDPRConsentString("1")
            # appOptions.setGDPRRequired(True)
            #
            # adcolony = autoclass("com.adcolony.sdk.AdColony")
            # AdColony = adcolony()
            # jString = autoclass('java.lang.String')
            # AdColony.configure(currentActivity, appOptions, jString("app5cf2981d26c14dd4a9"), jString("vz4458ff2a0207406b8b"))
            AdColonyMediationAdapter = autoclass("com.google.ads.mediation.adcolony.AdColonyMediationAdapter")
            appOptions = AdColonyMediationAdapter.getAppOptions()
            appOptions.setGDPRConsentString("1")
            appOptions.setGDPRRequired(True)
            print(appOptions.getGDPRRequired())

            from kivmob import KivMob

            self.ads = KivMob('ca-app-pub-9614085129932704~9292191302')
            self.ads.new_interstitial('ca-app-pub-9614085129932704/7878488547')

            # self.ads = KivMob(TestIds.APP)
            # self.ads.new_interstitial(TestIds.INTERSTITIAL)

            self.ads.request_interstitial()

            # AMAZON ADS
            AdRegistration = autoclass("com.amazon.device.ads.AdRegistration")
            AdRegistration.enableLogging(True)
            # AdRegistration.enableTesting(True)
            AdRegistration.setAppKey("1d71349359254e938b7d7c34f41a0395")

            interstitialAd = autoclass("com.amazon.device.ads.InterstitialAd")
            self.InterstitialAd = interstitialAd(context)
            self.InterstitialAd.loadAd()


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

        # SET FONTS
        self.set_fonts()
        # self.add_main_widgets()

        # SEARCH FOR SONGS FROM THE GIVEN PATHS
        # self.config.add_callback(self.fetch_songs_from_local, 'search-paths', 'folders')
        #self.fetch_songs_from_local()
        # Clock.schedule_once(lambda x: db_main.initialize(self.config))
        Clock.schedule_once(self.initialize_db)

        from screens.main import MainScreen
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main_screen'))
        return self.sm

    def initialize_db(self, *args):
        db_main.initialize(self.config)
        self.all_songs = get.all_songs()

    def add_main_widgets(self, *args):
        print(self.root.ids)
        if platform not in ['android', 'ios']:
            '''
            IN DESKTOPS, set the navigation drawer in a fixed position hence :
            * remove menu_btn
            * remove nav_items and app_logo from nav_drawer and add it to main_layout
            '''
            self.root.ids.top_bar_box.remove_widget(self.root.ids.menu_btn)

            nav_card = MDCard(orientation='vertical',
                            size_hint= (0.2, 0.99),
                            border_radius=dp(50),
                            pos_hint={'x': 0.005, 'center_y': 0.5})
            self.root.ids.main_layout.add_widget(nav_card)

            _nav_items = self.root.ids.nav_items
            _app_logo = self.root.ids.app_logo
            self.root.ids.nav_drawer.remove_widget(_nav_items)
            self.root.ids.nav_drawer.remove_widget(_app_logo)
            # self.root.ids.main_layout.add_widget(_nav_items)
            # self.root.ids.main_layout.add_widget(_app_logo)
            nav_card.add_widget(_app_logo)
            nav_card.add_widget(_nav_items)

            self.root.ids.nav_layout.size_hint_x = 0.8
            # _nav_items.size_hint_x = 0.25

    def fetch_songs_from_local(self, *args):
        from libs.media.mediafile import MediaFile

        config = self.config
        folders = str(config.get('search-paths', 'folders')).split(',')
        if '/' in folders:
            folders.remove('/')
        id = 0
        for folder in folders:
            for format in ["mp3", "aac", "3gp", "flac", "mkv", "wav", "ogg", "m4a"]:
                for file in pathlib.Path(folder).rglob(f'*.{format}'):
                    path = str(file)
                    audio_file = MediaFile(file)

                    if platform == 'win':
                        path = path.replace('/', '\\')

                    self.all_songs[id] = {
                        'id': id,
                        'album': audio_file.tags['album'],
                        'artist': audio_file.tags['artist'],
                        'path': path,
                        'name': audio_file.tags['name'] if audio_file.tags['name'] != 'None' else file.stem,
                        'extension': file.suffix,
                        'artwork': self.extract_song_artwork(file, id),
                        'length': audio_file.info['length']
                    }
                    id += 1

    def set_fonts(self, *args):
        from kivymd.font_definitions import theme_font_styles
        LabelBase.register(
            name="OpenSans",
            fn_regular="assets/fonts/OpenSans-Regular.ttf",
            fn_italic="assets/fonts/OpenSans-Italic.ttf",
            fn_bold="assets/fonts/OpenSans-Bold.ttf",
            fn_bolditalic="assets/fonts/OpenSans-BoldItalic.ttf")

        theme_font_styles.append('OpenSans')
        self.theme_cls.font_styles['OpenSans'] = [
            "OpenSans",
            16,
            False,
            0.15,
        ]

    def send_all_songs(self, *args):
        all_songs_new = self.all_songs
        for id in all_songs_new.keys():
            if 'artwork' in all_songs_new[id]: del all_songs_new[id]['artwork']

        print(all_songs_new)

        self.remote_client.send_message(b'/set_remote_songs', [json.dumps(all_songs_new).encode('utf8'), ])

    def set_remote_id(self, message, *args):
        self.remote_id = message.decode('utf8')

    def set_remote_songs(self, message, *args):
        remote_songs = message.decode('utf8')
        print(remote_songs)
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

        pathlib.Path('remote_temp').mkdir(exist_ok=True)

        with open(f"remote_temp/{song_name}.mp3", "wb") as f:
            packet = client_socket.recv(buffer_size)
            while len(packet) != 0:
                f.write(packet)
                packet = client_socket.recv(buffer_size)

        s.close()

        song_path = f'remote_temp/{song_name}.mp3'

        self.all_songs['remote'] = {
            'id': 'remote',
            'path': song_path,
            'name': song_name,
            # 'artwork':
        }
        Clock.schedule_once(partial(self.extract_song_artwork, song_path, 'remote'))
        Clock.schedule_once(self.play_remote_song, 2)

    def play_remote_song(self, *args):
        # while self.all_songs['remote']['artwork'] is None:
        #     pass
        self.now_playing = self.all_songs['remote']
        print(self.now_playing)

        screen_name = 'song_screen'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            from screens.song import SongScreen
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
    if platform not in ['android', 'ios']:
        Window.maximize()
    app = MainApp()
    app.run()
