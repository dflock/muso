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

from titlecase import titlecase

# from hsaudiotag import auto


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
        has_folder_jpg = False
        only_contains_folders = True

        for item in files:
            item_path = join(path, item)
            if is_image_file(item_path):
                has_art = True
                if is_folder_art(item):
                    has_folder_jpg = True
            elif not (isdir(item_path) or is_ignored_file(item_path)):
                only_contains_folders = False

    return {
        'ok': has_art and only_contains_folders and has_folder_jpg,
        'has_art': has_art and has_folder_jpg,
        'only_contains_folders': only_contains_folders
    }


def check_album_folder(path):
    """
    Check that the given path looks like an Album folder should:

    - has a folder.jpg, possibly more than one image, but no music.
    - otherwise, only contains music, or certain .log/.cue type files that are ignored.
    """

    if isdir(path):
        contents = os.listdir(path)
        contents = filter(lambda x: isfile(join(path, x)) and not x.startswith('.'), contents)

        has_album_art = False
        has_folder_jpg = False
        only_contains_music = True
        folder_has_date = False
        folder_has_cd = False
        folder_has_spaces = False
        folder_titlecase = True
        music_consistent = True

        if re_folder_date.match(path):
            # Folder name contains a date-a-like: (1999)
            folder_has_date = True

        if re_folder_cd.match(path):
            # Folder name contains a CD-a-like: [cd 1]
            folder_has_cd = True

        if re_folder_space.match(path):
            # Folder name starts with a space, has multiple spaces, or ends with a space.
            folder_has_spaces = True

        for item in contents:
            item_path = join(path, item)
            if is_image_file(item_path):
                has_album_art = True
                if is_folder_art(item):
                    has_folder_jpg = True
            elif is_music_file(item_path):
                # Further check music file for consistency
                if not check_music_file(item_path):
                    music_consistent = False
            elif not (is_music_file(item_path) or is_ignored_file(item_path)):
                only_contains_music = False

        album_folder = os.path.split(path)[1]
        if album_folder != titlecase(album_folder):
            folder_titlecase = False

    return {
        'ok': has_album_art and has_folder_jpg and only_contains_music and not folder_has_date and not folder_has_cd and not folder_has_spaces and music_consistent and folder_titlecase,
        'has_album_art': has_album_art and has_folder_jpg,
        'only_contains_music': only_contains_music,
        'music_consistent': music_consistent,
        'folder_has_date': folder_has_date,
        'folder_has_cd': folder_has_cd,
        'folder_has_spaces': folder_has_spaces,
        'folder_titlecase': folder_titlecase
    }


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


def is_folder_art(file):
    """
    Is file called folder.jpg
    TODO: Is it at least 500px square?
    """
    if re_folder_jpeg.match(os.path.basename(file)):
        return True


def is_ignored_file(file):
    """
    Can we ignore this file and pretend it isn't there?
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
    album, filename = os.path.split(file)
    artist, album = os.path.split(album)
    artist = os.path.split(artist)[1]

    # print 'path: ' + file
    # print 'artist: ' + artist
    # print 'album: ' + album
    # print 'filename: ' + filename
    # print '----------------------'

    # Don't require any of the following reserved characters to be in the filename, even if they're in the metadata:
    #     < (less than)
    #     > (greater than)
    #     : (colon)
    #     " (double quote)
    #     / (forward slash)
    #     \ (backslash)
    #     | (vertical bar or pipe)
    #     ? (question mark)
    #     * (asterisk)

    illegal_chars = re.compile(r'\<|\>|\:|\"|\/|\||\?|\*|\\')
    artist = illegal_chars.sub('.', artist)
    album = illegal_chars.sub('.', album)

    general_album = re.compile(artist + ' - ' + album + ' - \d+\.\d+ - .*', re.IGNORECASE)
    compilation_album = re.compile(album + ' - \d+\.\d+ - ' + artist + ' - .*', re.IGNORECASE)

    return general_album.match(filename) or compilation_album.match(filename)


def render_artist_output_plain_text(artist, status):

    str_status = ''
    str_status += render_value_plain_text(status['only_contains_folders'])
    str_status += render_value_plain_text(status['has_art'])

    tmp = '\n'
    tmp += artist.ljust(57, ' ') + str_status + '\n'
    tmp += ''.ljust(55, '-') + ' Cruft '.ljust(10, '-') + ' Art '.ljust(10, '-') + ' F.Date '.ljust(10, '-') + ' F.CD '.ljust(10, '-') + ' F.Space '.ljust(10, '-') + ' F.Title '.ljust(10, '-') + ' M.Cons '.ljust(10, '-')
    tmp += '\n'

    return tmp


def render_album_output_plain_text(album, status):

    str_status = ''
    str_status += render_value_plain_text(status['only_contains_music'])
    str_status += render_value_plain_text(status['has_album_art'])
    str_status += render_value_plain_text(not status['folder_has_date'])
    str_status += render_value_plain_text(not status['folder_has_cd'])
    str_status += render_value_plain_text(not status['folder_has_spaces'])
    str_status += render_value_plain_text(status['folder_titlecase'])
    str_status += render_value_plain_text(status['music_consistent'])

    album_name = (album[:50] + '..') if len(album) > 50 else album

    return album_name.ljust(57) + str(str_status) + '\n'


def render_value_plain_text(val, width=12):
    if val:
        tmp = '✓'.ljust(width)
    else:
        tmp = '✗'.ljust(width)

    return tmp


# Initialization stuff

mimetypes.init()
mimetypes.add_type('application/x-cue', '.cue', strict=True)
mimetypes.add_type('text/x-log', '.log', strict=True)
mimetypes.add_type('application/x-sfv', '.sfv', strict=True)

re_folder_date = re.compile('.*\(\d{2,4}\).*')
re_folder_cd = re.compile('.*\[?(cd|disk).*\]?.*', re.IGNORECASE)
re_folder_space = re.compile('^ .*|.*  .*|.* $')
re_folder_jpeg = re.compile('folder.jpe?g', re.IGNORECASE)

root = os.path.expanduser('~') + '/Music'
# root = '/home/duncan/tmp/muso'
artist_tmp = ''
tmp = ''
output = ''

artist_count = 0
album_count = 0

music = build_file_tree(root)

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
