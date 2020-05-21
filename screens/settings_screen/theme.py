from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.uix.picker import MDThemePicker

from kivy.lang.builder import Builder

from functools import partial

Builder.load_string('''
<SettingsThemeScreen>:
    id: theme_settings
    name: 'theme_settings'
    BoxLayout:
        orientation: 'vertical'

        ScrollView:
            MDList:
                TwoLineIconListItem:
                    text: "Colors"
                    secondary_text: "theme, accent, style"
                    on_press: root.open_theme_picker()

                    IconLeftWidget:
                        icon: 'format-color-fill'
''')

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
