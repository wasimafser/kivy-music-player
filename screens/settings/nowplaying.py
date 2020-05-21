from kivy.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog

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
