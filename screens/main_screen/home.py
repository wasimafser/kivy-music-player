from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem

from kivy.utils import platform
from kivy.lang.builder import Builder

from plyer import storagepath
if platform == 'android':
    from android.permissions import request_permissions, Permission

Builder.load_string('''
<HomeScreen>:
    AnchorLayout:
        MDLabel:
            text: "WILL BE POPULATED SOON"
            theme_text_color: "Hint"
            font_style: "Button"
            halign: 'center'
            position: {'center_x': 0.5, 'center_y': '0.5'}

        # MDFlatButton:
        #     text: "LOAD AD"
        #     on_release: root._load_ad()
''')

class HomeScreen(MDBottomNavigationItem):
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            # self.app.ads.show_interstitial()
        self.app.client.send_message(b'/print_api', ['in home_screen'.encode('utf8'), ])
