from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen

from kivy.lang.builder import Builder

Builder.load_string('''
<SettingsScreen>:
    id: settings_screen
    BoxLayout:
        orientation: 'vertical'

        MDToolbar:
            title: "Settings"
            left_action_items: [["arrow-left", lambda x: root.go_to_main()]]

        ScrollView:

            MDList:
                id: settings_list

                TwoLineIconListItem:
                    text: "Search Paths"
                    secondary_text: "where to look for songs"
                    on_press: root.go_to_search_paths()

                    IconLeftWidget:
                        icon: 'folder-search'

                TwoLineIconListItem:
                    text: "App Theme"
                    secondary_text: "change the looks of the app"
                    on_press: root.go_to_themes()

                    IconLeftWidget:
                        icon: 'format-color-fill'

                TwoLineIconListItem:
                    text: "Now Playing"
                    secondary_text: "change the looks of the now-playing screen"
                    on_press: root.go_to_now_playing()

                    IconLeftWidget:
                        icon: 'play-circle-outline'
''')

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
            from screens.settings_screen.theme import SettingsThemeScreen
            self.sm.add_widget(SettingsThemeScreen())

    def go_to_now_playing(self, *args):
        screen_name = 'now_playing_settings'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            from screens.settings_screen.nowplaying import SettingsNowPlayingScreen
            self.sm.add_widget(SettingsNowPlayingScreen())

    def go_to_search_paths(self, *args):
        screen_name = 'settings_search_paths'
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        else:
            from screens.settings_screen.searchpaths import SettingsSearchPathsScreen
            self.sm.add_widget(SettingsSearchPathsScreen())
