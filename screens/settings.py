from kivy.app import MDApp
from kivy.uix.screenmanager import Screen

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
