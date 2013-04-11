# -*- coding: utf-8 -*-

"""
muso
========================

The Music Collection Auditor

"""
import os
from os.path import join
from os.path import isdir
from os.path import isfile

import mimetypes


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

    - has a folder.jpg, possibly more than one image, but no music.
    - otherwise, only contains folders, which contain music
    """
    pass


def check_album_folder(path):
    """
    Check that the given path looks like an Album folder should:

    - has a folder.jpg
    - otherwise, only contains music
    """

    if isdir(path):
        contents = os.listdir(path)
        contents = filter(lambda x: isfile(join(path, x)) and not x.startswith('.'), contents)

        has_album_art = False
        only_contains_music = True

        for item in contents:
            item_path = join(path, item)
            if is_image_file(item_path):
                has_album_art = True
            elif not (is_music_file(item_path) or is_ignored_file(item_path)):
                only_contains_music = False

    # return has_album_art and only_contains_music
    return {'ok': has_album_art and only_contains_music, 'has_album_art': has_album_art, 'only_contains_music': only_contains_music}


def is_music_file(file):
    """
    Is file a music file?
    """
    try:
        return mimetypes.guess_type(file)[0].startswith('audio')
    except AttributeError:
        return False


def is_image_file(file):
    """
    Is file an image file?
    """
    try:
        return mimetypes.guess_type(file)[0].startswith('image')
    except AttributeError:
        return False


def is_ignored_file(file):
    """
    Can we ignore this file and pretend that it wasn't there?
    """
    try:
        return mimetypes.guess_type(file)[0] in ('application/x-cue', 'text/x-log', 'application/x-sfv')
    except AttributeError:
        return False


def check_music_file(file):
    """
    Check that the given file looks like a music file should:

    - is an mp3|flac|ogg file
    - filename matches one of these:
        - Compilation Albums: <album> - <discnumber>.<tracknumber> - <artist> - <title>.ext
        - Regular Albums:     <artist> - <album> - <discnumber>.<tracknumber> - <title>.ext
    - Check tags
    """
    pass

# TODO: Maybe add extra mimitypes for .log, .cue, etc... files.
mimetypes.init()
mimetypes.add_type('application/x-cue', '.cue', strict=True)
mimetypes.add_type('text/x-log', '.log', strict=True)
mimetypes.add_type('application/x-sfv', '.sfv', strict=True)

root = os.path.expanduser('~') + '/Music'
music = build_file_tree(root)
tmp = ''
output = ''

for artist in music.keys():
    tmp += "\n"
    tmp += '[' + artist + '] Ablums:\n'
    tmp += '------------------------\n'
    for album in music[artist]:
        status = check_album_folder(join(root, artist, album))
        if status['ok'] is False:
            tmp += album.ljust(80) + ' ' + str(status) + '\n'
            output += tmp
        else:
            tmp = ''

        # if check_album_folder(join(root, artist, album)):
        #     tmp += album + ' ✓'
        # else:
        #     tmp += album + ' ✗'

print output
