from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.uix.screenmanager import Screen
from kivymd.uix.filemanager import MDFileManager

from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.utils import platform

Builder.load_string('''
<ItemWithRemove>:

    IconRightWidget:
        icon: 'minus'

<SettingsSearchPathsScreen>:
    name: 'settings_search_paths'
    BoxLayout:
        orientation: 'vertical'

        ScrollView:

            MDList:
                id: search_paths_list

        MDBottomAppBar:
            MDToolbar:
                title: "Search Paths"
                icon: "plus"
                type: 'bottom'
                left_action_items: [["arrow-left", lambda x: root.go_to_settings()]]
                on_action_button: root.launch_file_manager()
                mode: 'end'
''')

class ItemWithRemove(OneLineAvatarIconListItem):
    pass

class SettingsSearchPathsScreen(Screen):
    search_path_items = ListProperty()

    def __init__(self, *args, **kwargs):
        super(SettingsSearchPathsScreen, self).__init__(*args, **kwargs)
        self.config = MDApp.get_running_app().config
        self.search_paths = str(self.config.get('search-paths', 'folders')).split(',')

        for path in self.search_paths:
            item = ItemWithRemove(
                text = path
            )
            self.search_path_items.append(item)

        Clock.schedule_once(self.populate_list)

    def populate_list(self, *args):
        for item in self.search_path_items:
            self.ids.search_paths_list.add_widget(item)

    def go_to_settings(self, *args):
        MDApp.get_running_app().sm.current = 'settings_screen'

    def launch_file_manager(self, *args):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            # previous=True,
        )
        default_path = '/'
        if platform == 'android':
            default_path = '/storage/emulated/0'
        self.file_manager.show(default_path)

    def select_path(self, path):
        self.exit_manager()
        self.search_paths.append(path)
        all_paths = ','.join(self.search_paths)
        self.config.set('search-paths', 'folders', all_paths)
        self.config.write()

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()
