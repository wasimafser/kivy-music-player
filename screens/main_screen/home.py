from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.card import MDCard

from kivy.utils import platform
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

from plyer import storagepath
if platform == 'android':
    from android.permissions import request_permissions, Permission

from libs.database.get import all_artists

Builder.load_string('''
<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        RecycleView:
            id: artists_rv
            viewclass: 'ArtistCard'
            size_hint_y: 0.3
            do_scroll_x: True
            do_scroll_y: False
            RecycleBoxLayout:
                orientation: 'horizontal'
                padding: [10, 10, 10, 10]
                default_size_hint: None, 1
                default_size: self.height, None
                size_hint_x: None
                width: self.minimum_width
        MDLabel:
            text: "WILL BE POPULATED SOON"
            theme_text_color: "Hint"
            font_style: "OpenSans"
            halign: 'center'
            position: {'center_x': 0.5, 'center_y': '0.5'}

        # MDFlatButton:
        #     text: "LOAD AMAZON AD"
        #     on_release: root._load_ad('amazon')
        #
        # MDFlatButton:
        #     text: "LOAD ADMOB AD"
        #     on_release: root._load_ad('admob')

<ArtistCard>:
    orientation: 'vertical'
    MDCard:
        size_hint_x: None
        pos_hint: {'center_x': 0.5}
        width: self.height
        FitImage:
            texture: root.image
    MDLabel:
        text: root.name
        halign: 'center'
        size_hint_y: 0.15
        font_style: 'OpenSans'
        theme_text_color: 'Primary'
''')

class ArtistCard(BoxLayout):
    id = NumericProperty()
    image = ObjectProperty()
    name = StringProperty()

    def __init__(self, *args, **kwargs):
        super(ArtistCard, self).__init__(*args, **kwargs)


class HomeScreen(MDBottomNavigationItem):
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        Clock.schedule_once(self.update_widgets)

        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        try:
            self.app.client.send_message(b'/print_api', ['in home_screen'.encode('utf8'), ])
        except Exception as e:
            print(e)

    def update_widgets(self, *args):
        self.ids.artists_rv.data = all_artists()

    def _load_ad(self, source, *args):
        if source == 'admob':
            self.app.ads.show_interstitial()
        else:
            self.app.InterstitialAd.showAd()
