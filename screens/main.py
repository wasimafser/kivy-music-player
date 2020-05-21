from kivy.app import MDApp
from kivy.uix.screenmanager import Screen

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
