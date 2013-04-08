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


music = build_file_tree(os.path.expanduser('~') + '/Music')

for artist in music.keys():
    print
    print '[' + artist + '] Ablums:'
    print '------------------------'
    for album in music[artist]:
        print album
