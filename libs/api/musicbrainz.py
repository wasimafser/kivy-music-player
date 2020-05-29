import musicbrainzngs
import requests

musicbrainzngs.set_useragent('Matrix Music Player', '0.1', 'wasim.afser@gmail.com')
musicbrainzngs.auth('wasimafser', 'w@sim0206')

def get_artist_info(artist, search=False):
    artist_info = {
        'mb_id': None,
        'image': None
    }
    if search:
        search_result = musicbrainzngs.search_artists(query=artist, limit=1)
        result = search_result['artist-list'][0]
        if result['name'] == artist:
            artist_info['mb_id'] = result['id']

            search_result = musicbrainzngs.get_artist_by_id(
                                artist_info['mb_id'],
                                includes=["url-rels"]
                            )

            result = search_result['artist']['url-relation-list']
            for rel in result:
                if rel['type'] == 'image':
                    image_data = requests.get(rel['target'])
                    print(image_data.content)
                    # artist_info['image'] =
                    # return artist_info
