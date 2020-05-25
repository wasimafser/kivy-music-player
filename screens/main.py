from kivymd.app import MDApp

from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder

Builder.load_string('''
#:import HomeScreen screens.main_screen.home.HomeScreen
#:import SongListScreen screens.main_screen.songlist.SongListScreen
#:import SPlayScreen screens.main_screen.splay.SPlayScreen

<MainScreen>:
    id: main_screen
    FloatLayout:
        id: main_layout

        BoxLayout:
            id: top_bar
            size_hint: 0.9, 0.05
            pos_hint: {'center_x': 0.5, 'top': 1}

            # StackLayout:
            BoxLayout:
                id: top_bar_box
                # orientation: 'lr-tb'
                orientation: 'horizontal'

                MDIconButton:
                    id: menu_btn
                    icon: 'menu'
                    on_release: nav_drawer.toggle_nav_drawer()

                TextInput:
                    multiline: False
                    padding: [0, (self.height-self.line_height)/2]
                    background_normal: 'assets/transparent.png'
                    background_active: 'assets/transparent.png'
                    hint_text: 'Search'

                MDIconButton:
                    id: settings_btn
                    icon: 'settings'
                    pos_hint: {'right': 1}
                    on_release: root.go_to_settings()

        NavigationLayout:
            id: nav_layout
            pos_hint: {'right': 1}
            # canvas.before:
            #     Color:
            #         rgba: (1, 0, 0, 1)
            #     Rectangle:
            #         size: self.size
            #         pos: self.pos

            ScreenManager:
                size_hint_y: 0.95
                id: sm
                pos_hint: {'right': 1}

                HomeScreen:
                    name: "home_screen"

                SongListScreen:
                    name: "song_list_screen"



            MDNavigationDrawer:
                id: nav_drawer
                orientation: 'vertical'
                on_state:
                    # menu_btn.opacity = 1 if self.state == 'close' else 0
                    menu_btn.opacity = 1 if self.state == 'close' else 0

                BoxLayout:
                    id: app_logo
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: avatar.height

                    Image:
                        id: avatar
                        size_hint: None, None
                        size: "56dp", "56dp"
                        source: "assets/icon.png"

                    MDLabel:
                        text: 'MATRIX MUSIC PLAYER'
                        font_style: 'OpenSans'
                        halign: 'center'
                        valign: 'center'

                ScrollView:
                    id: nav_items
                    MDList:
                        OneLineListItem:
                            text: 'YOUR LIBRARY'
                            font_style: 'OpenSans'
                        OneLineIconListItem:
                            text: 'Home'
                            divider: None
                            on_release: sm.current = 'home_screen'

                            IconLeftWidget:
                                icon: 'home'

                        OneLineIconListItem:
                            text: 'Songs'
                            divider: None
                            on_release: sm.current = 'song_list_screen'

                            IconLeftWidget:
                                icon: 'music'
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
