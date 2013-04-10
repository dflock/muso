"""
muso
========================

The Music Collection Auditor

"""
import os
from os.path import join
from os.path import isdir


def build_file_tree(root):
    """
    Build a dictionary that mirrors the file system hierarcy inside the given root.

    <start_dir>/artist/album/track.mp3
    """

    tree = {}
    for item in os.listdir(root):
        current_item = join(root, item)
        if isdir(current_item):
            sub_items = os.listdir(current_item)
            tree[item] = filter(lambda x: isdir(join(current_item, x)) and not x.startswith('.'), sub_items)
    return tree


def check_artist_folder(path):
    """
    Check that the given path looks like an Artist folder should:

    - has a folder.jpg
    - otherwise, only contains folders, which contain music
    """
    pass


def check_album_folder(path):
    """
    Check that the given path looks like an Album folder should:

    - has a folder.jpg
    - otherwise, only contains music
    """
    pass


def check_music_file(file):
    """
    Check that the given path looks like a music file should:

    - is an mp3|flac|ogg file
    - filename matches one of these:
        - Compilation Albums: <album> - <discnumber>.<tracknumber> - <artist> - <title>.ext
        - Regular Albums:     <artist> - <album> - <discnumber>.<tracknumber> - <title>.ext
    - Check tags
    """
    pass


music = build_file_tree(os.path.expanduser('~') + '/Music')

for artist in music.keys():
    print
    print '[' + artist + '] Ablums:'
    print '------------------------'
    for album in music[artist]:
        print album
