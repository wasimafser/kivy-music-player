from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty

import socket
import os
import threading

from oscpy.client import OSCClient

Builder.load_string('''
<SPlayScreen>:
    id: splay_screen
    BoxLayout:
        orientation: "vertical"

        ScrollView:
            MDList:
                id: songs_list

        MDFloatingActionButton:
            id: display_id
            icon: "remote"
            md_bg_color: app.theme_cls.primary_color
            on_release: root.show_id()


<SPDialogContent>:
    orientation: "vertical"
    size_hint_y: None
    spacing: "10dp"

    MDLabel:
        text: 'Your ID'
        theme_text_color: "Hint"
        font_style: 'Subtitle1'

    MDLabel:
        text: root.id
        theme_text_color: "Primary"
        halign: 'center'
        font_style: 'H6'

    MDSeparator:
        height: "2dp"

    MDLabel:
        text: 'Enter the id displayed in another device'
        theme_text_color: "Hint"
        font_style: 'Subtitle2'

    MDTextField:
        id: remote_id
        hint_text: "Enter ID"


''')

class RemoteSongItem(OneLineListItem):
    song_id = NumericProperty()
    pass


class SPDialogContent(BoxLayout):
    id = StringProperty('')

    def set_id(self, id_dialog):
        self.app = MDApp.get_running_app()
        self.app.remote_id = self.ids.remote_id.text
        return id_dialog.dismiss()

class SPlayScreen(MDBottomNavigationItem):

    def connect(self, ip_range, subnet):
        print(range(ip_range[0], ip_range[1]))
        for ip in range(ip_range[0], ip_range[1]):
            hostaddr = f"{subnet}.{ip}"
            result = os.system(f"ping -c 1 {hostaddr} >/dev/null") == 0
            if result:
                print(hostaddr)

    def look_for_music_player(self, *args):
        s_ip = self.self_ip.split('.')
        subnet = '.'.join([s_ip[0], s_ip[1], s_ip[2]])

        ip_range = [0, 12]
        for i in range(20):
            thread = threading.Thread(target=self.connect, args=(ip_range, subnet, ))
            thread.start()
            ip_range[0] = ip_range[1]
            ip_range[1] = ip_range[1]+12
            if ip_range[1] > 255:
                ip_range[1] == 255

    def __init__(self, *args, **kwargs):
        super(SPlayScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

        try:
            self.self_ip = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            self.self_ip = socket.gethostbyname("")

        if self.self_ip.startswith("127.") or self.self_ip.startswith("0."):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.self_ip = s.getsockname()[0]
            s.close()

        # Clock.schedule_once(self.look_for_music_player)
        self.app.bind(remote_songs = self.load_songs)

    def load_song(self, *args):
        instance = args[0]
        # song = self.app.remote_songs[f'{instance.song_id}']
        # self.app.remote_client.send_message(b'/send_song', [song['path'].encode('utf8'), ])
        self.app.remote_client.send_message(b'/send_song', [f'{instance.song_id}'.encode('utf8'), ])

    def load_songs(self, *args):
        if self.app.remote_id != self.self_ip:
            for id in self.app.remote_songs.keys():
                song = self.app.remote_songs[id]
                item = RemoteSongItem(
                    text= song['name'],
                    on_release= self.load_song,
                )
                item.song_id = int(id)
                # item.ids.artwork_thumb.texture = item.artwork = song['artwork']
                self.ids.songs_list.add_widget(item)

    def get_remote_songs(self, *args):
        remote_id = self.app.remote_id
        if remote_id != '':
            # self.app.set_remote_client()
            self.app.remote_client.send_message(b'/set_remote_id', [self.self_ip.encode('utf8'),])
            self.app.remote_client.send_message(b'/send_all_songs', [])

    def show_id(self, *args):
        id_dialog = MDDialog(
            title="Share Play",
            type="custom",
            auto_dismiss=False,
            content_cls=SPDialogContent(id=self.self_ip),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: id_dialog.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: id_dialog.content_cls.set_id(id_dialog)
                ),
            ],
        )
        id_dialog.open()
        id_dialog.bind(on_dismiss=self.get_remote_songs)
