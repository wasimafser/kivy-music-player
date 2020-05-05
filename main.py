import os
os.environ['KIVY_AUDIO'] = "ffpyplayer"

from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, DictProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

import glob
import pathlib

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

class SongItem(OneLineAvatarIconListItem):
    song_id = NumericProperty()

class SongListScreen(MDBottomNavigationItem):
    all_songs = DictProperty()

    def __init__(self, *args, **kwargs):
        super(SongListScreen, self).__init__(*args, **kwargs)
        paths = MDApp.get_running_app().songs
        id = 0
        for path in paths:
            self.all_songs[id] = {
                'path': path,
                'name': pathlib.Path(path).stem
            }
            id += 1

        Clock.schedule_once(self.populate_song_list)

    def populate_song_list(self, *args):
        for id in self.all_songs.keys():
            item = SongItem(
                text= self.all_songs[id]['name'],
                on_release= self.play_song
            )
            item.song_id = id
            self.ids.songs_list.add_widget(item)

    def play_song(self, *args):
        song_path = self.all_songs[args[0].song_id]['path']

        self.song = SoundLoader.load(song_path)
        if self.song:
            self.song.play()
            Clock.schedule_interval(self.manage_song, 1)

    def manage_song(self, *args):
        print(self.song.get_pos(), self.song.length)


class MainApp(MDApp):
    songs = ListProperty()

    def build(self):
        # SEARCH FOR SONGS FROM THE GIVEN PATHS
        config = self.config
        folders = str(config.get('search_paths', 'folders')).split(',')
        for folder in folders:
            for file in glob.glob(f"{folder}/*.mp3"):
                self.songs.append(file)

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
