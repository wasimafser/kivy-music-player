from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineListItem

from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

from functools import partial

Builder.load_string('''
<SettingsNowPlayingScreen>:
    name: 'now_playing_settings'
    BoxLayout:
        orientation: 'vertical'

        ScrollView:

            MDList:
                TwoLineIconListItem:
                    text: "Background"
                    secondary_text: "background of the now playing screen"
                    on_press: root.open_background_selector()

                    IconLeftWidget:
                        icon: 'format-color-fill'
''')

class SettingsNowPlayingScreen(Screen):
    dialog = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(SettingsNowPlayingScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.config = self.app.config

    def set_now_playing_background(self, bg, *args):
        self.app.now_playing_background = bg
        self.config.set('now-playing', 'background', bg)
        self.config.write()

        self.dialog.dismiss()

    def open_background_selector(self, *args):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Choose background",
                type="simple",
                items=[
                    TwoLineListItem(text="Default", secondary_text="the default theme background", on_touch_down=partial(self.set_now_playing_background, 'default')),
                    TwoLineListItem(text="Artwork Color", secondary_text="the dominant color from artwork", on_touch_down=partial(self.set_now_playing_background, 'artwork-color')),
                ],
            )
        self.dialog.open()
