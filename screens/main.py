from kivymd.app import MDApp

from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder

Builder.load_string('''
#:import HomeScreen screens.main_screen.home.HomeScreen
#:import SongListScreen screens.main_screen.songlist.SongListScreen
#:import SPlayScreen screens.main_screen.splay.SPlayScreen

<MainScreen>:
    id: main_screen
    BoxLayout:
        orientation: "vertical"

        MDToolbar:
            id: main_toolbar
            title: "Matrix Music Player"
            font_style: 'OpenSans'
            # right_action_items: [["settings", lambda x: root.go_to_settings()]]

            MDIconButton:
                id: settings_btn
                icon: 'settings'
                on_release: root.go_to_settings()

        MDBottomNavigation:

            HomeScreen:
                name: "home_screen"
                text: 'Home'
                icon: 'home'

            SongListScreen:
                name: "song_list_screen"
                text: 'Songs'
                icon: 'music'

            SPlayScreen:
                name: "splay_screen"
                text: 'SPLAY'
''')


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
            from screens.settings import SettingsScreen
            sm.add_widget(SettingsScreen(name=screen_name))
