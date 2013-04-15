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

import re

import mimetypes

from hsaudiotag import auto


def build_file_tree(root):
    """
    Build a dictionary that mirrors the file system hierarcy inside the given root.

    <root>/artist/album/track.mp3
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
    - otherwise, only contains folders
    """

    if isdir(path):
        contents = os.listdir(path)
        files = filter(lambda x: isfile(join(path, x)) and not x.startswith('.'), contents)

        has_art = False
        only_contains_folders = True

        for item in files:
            item_path = join(path, item)
            if is_image_file(item_path):
                # This needs to specifically check for folder.jpg too, because it's special.
                has_art = True
            elif not (isdir(item_path) or is_ignored_file(item_path)):
                only_contains_folders = False

    return {
        'ok': has_art and only_contains_folders,
        'has_art': has_art,
        'only_contains_folders': only_contains_folders
    }


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
        folder_has_date = False
        folder_has_cd = False
        folder_has_spaces = False

        folder_date = re.compile('.*\(\d{2,4}\).*')
        if folder_date.match(path):
            # Folder name contains a date-a-like: (1999)
            folder_has_date = True

        folder_cd = re.compile('.*\[?(cd|disk).*\]?.*', re.IGNORECASE)
        if folder_cd.match(path):
            # Folder name contains a CD-a-like: [cd 1]
            folder_has_cd = True

        folder_space = re.compile('^ .*|.*  .*|.* $')
        if folder_space.match(path):
            # Folder name starts with a space, has multiple spaces, or ends with a space.
            folder_has_spaces = True

        for item in contents:
            item_path = join(path, item)
            if is_image_file(item_path):
                # This needs to specifically check for folder.jpg too, because it's special.
                has_album_art = True
            elif not (is_music_file(item_path) or is_ignored_file(item_path)):
                only_contains_music = False

    return {
        'ok': has_album_art and only_contains_music and not folder_has_date and not folder_has_cd and not folder_has_spaces,
        'has_album_art': has_album_art,
        'only_contains_music': only_contains_music,
        'folder_has_date': folder_has_date,
        'folder_has_cd': folder_has_cd,
        'folder_has_spaces': folder_has_spaces
    }


def is_music_file(file):
    """
    Is file a music file?
    """
    try:
        return mimetypes.guess_type(file)[0].startswith('audio')
        # return mimetypes.guess_type(file)[0].startswith('audio') and check_music_file(file)
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
    music_file = auto.File(file)

    return music_file.valid


def render_artist_output_plain_text(artist, status):

    str_status = ''
    str_status += render_value_plain_text(status['only_contains_folders'])
    str_status += render_value_plain_text(status['has_art'])

    tmp = '\n'
    tmp += artist.ljust(57, ' ') + str_status + '\n'
    tmp += ''.ljust(55, '-') + ' Cruft '.ljust(10, '-') + ' Art '.ljust(10, '-') + ' F.Date '.ljust(10, '-') + ' F.CD '.ljust(10, '-') + ' F.Space '.ljust(10, '-')
    tmp += '\n'

    return tmp


def render_album_output_plain_text(album, status):

    str_status = ''
    str_status += render_value_plain_text(status['only_contains_music'])
    str_status += render_value_plain_text(status['has_album_art'])
    str_status += render_value_plain_text(not status['folder_has_date'])
    str_status += render_value_plain_text(not status['folder_has_cd'])
    str_status += render_value_plain_text(not status['folder_has_spaces'])

    album_name = (album[:50] + '..') if len(album) > 50 else album

    return album_name.ljust(57) + str(str_status) + '\n'


def render_value_plain_text(val, width=12):
    if val:
        tmp = '✓'.ljust(width)
    else:
        tmp = '✗'.ljust(width)

    return tmp


mimetypes.init()
mimetypes.add_type('application/x-cue', '.cue', strict=True)
mimetypes.add_type('text/x-log', '.log', strict=True)
mimetypes.add_type('application/x-sfv', '.sfv', strict=True)

root = os.path.expanduser('~') + '/Music'
# root = '/home/duncan/tmp/muso'
music = build_file_tree(root)
artist_tmp = ''
tmp = ''
output = ''

artist_count = 0
album_count = 0

for artist in music.keys():
    for album in music[artist]:
        artist_status = check_artist_folder(join(root, artist))
        album_status = check_album_folder(join(root, artist, album))
        if album_status['ok'] is False:
            tmp += render_album_output_plain_text(album, album_status)
            album_count += 1

    # this makes is complain about artist folders with no art in, which I'd like to see, but not now, there are too many of them.
    # if tmp or artist_status['ok'] is False:
    if tmp:
        output += render_artist_output_plain_text(artist, artist_status) + tmp
        tmp = ''
        artist_count += 1

print output
print str(artist_count) + ' Artists, ' + str(album_count) + ' Albums with issues.'
