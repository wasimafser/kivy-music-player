from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.uix.screenmanager import Screen
from kivymd.uix.filemanager import MDFileManager

from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.recycleview import RecycleView

Builder.load_string('''
<ItemWithRemove>:

    IconRightWidget:
        icon: 'minus'
        on_release: root.delete_path(root.text)

<PathsList>:
    id: paths_list
    viewclass: 'ItemWithRemove'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'

<SettingsSearchPathsScreen>:
    name: 'settings_search_paths'
    BoxLayout:
        orientation: 'vertical'

        # ScrollView:
        #
        #     MDList:
        #         id: search_paths_list

        PathsList:


        MDBottomAppBar:
            MDToolbar:
                title: "Search Paths"
                icon: "plus"
                type: 'bottom'
                left_action_items: [["arrow-left", lambda x: root.go_to_settings()]]
                on_action_button: root.launch_file_manager()
                mode: 'end'
''')

class PathsList(RecycleView):
    def __init__(self, *args, **kwargs):
        super(PathsList, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.config = self.app.config
        self.config.add_callback(self.update_paths, 'search-paths', 'folders')

        self.update_paths()

    def update_paths(self, *args):
        self.search_paths = str(self.config.get('search-paths', 'folders')).split(',')
        self.data = []

        for path in self.search_paths:
            self.data.append({'text': path})


class ItemWithRemove(OneLineAvatarIconListItem):
    def delete_path(self, *args):
        path_to_delete = args[0]
        config = MDApp.get_running_app().config
        search_paths = str(config.get('search-paths', 'folders')).split(',')
        try:
            search_paths.remove(path_to_delete)
        except Exception as e:
            print(e)
        finally:
            all_paths = ','.join(search_paths)
            config.set('search-paths', 'folders', all_paths)
            config.write()


class SettingsSearchPathsScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(SettingsSearchPathsScreen, self).__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.config = self.app.config
        self.search_paths = str(self.config.get('search-paths', 'folders')).split(',')

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
