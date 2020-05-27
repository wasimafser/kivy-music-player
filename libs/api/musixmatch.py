import requests

class MusixMatch(object):
    root_url = "https://api.musixmatch.com/ws/1.1"
    apikey = "3af40fe6c503fe9e62b84b806674f18a"

    def track_search(self, title):
        # response = requests.get(f"{self.root_url}/track.search?q_title={title}&apikey={self.apikey}")
        # print(response.json())

        response = requests.get(f"{self.root_url}/track.search?q={title}&apikey={self.apikey}")
        print(response.json())
