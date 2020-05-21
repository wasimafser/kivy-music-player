from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from plyer import storagepath
if platform == 'android':
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    from kivmob import KivMob, TestIds

class HomeScreen(MDBottomNavigationItem):
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            self.app.ads.show_interstitial()
        self.app.client.send_message(b'/print_api', ['in home_screen'.encode('utf8'), ])
