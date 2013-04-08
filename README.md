# muso - The Music Collection Auditor

Muso will audit a large digital music collection and check for consistency and proper structure - in both metadata/tags and file & folder names.

This script will do the following things, eventually:

## Assume the following folder structures:

	~/Music/artist/album/
	~/Music/Compilations/album/
	~/Music/Soundtracks/album/
	~/Music/Classical/album/ ?


Report folders that don't match.

## Check for & report on:

These are things that you might want to fix:

* Albums with any of the following tags not the same for each track:
	* album, albumartist, discnumber, genre, date
	* replaygain_album_gain, replaygain_album_peak
	* musicbrainz_albumid, musicbrainz_albumartistid
* Albums with '(YYYY)' in the folder name
* Albums with folder names that Aren't Title Case
* Compilation albums that don't have albumartists set to 'Various Artists'
* Tracks missing any of the following tags:
	* album, artist, albumartist, tracknumber, discnumber, title, genre, date
	* replaygain_album_gain, replaygain_album_peak, replaygain_track_gain, replaygain_track_peak
	* musicbrainz_albumid, musicbrainz_albumartistid, musicbrainz_trackid
* A folder.jpeg|jpg in each album & artist folder, of at least 500x500px
* Extraneous .m3u, .info, .sfv, etc... files.
* The following filename structures:
	* Compilation Albums: <album> - <discnumber>.<tracknumber> - <artist> - <title>.ext
	* Regular Albums:     <artist> - <album> - <discnumber>.<tracknumber> - <title>.ext
* Genre issues:
	* Genre's with small number of tracks/ one track/ablum in
	* Unknown genre's/malformed genre tags

## Report on:

These are more statistical/informational:

* Total numbers of: tracks, albums, artists, genre's, total collection size in GB
* Breakdown of file formats: mp3/flac/ogg/etc
* Breakdown of bitrates for mp3/ogg/etc
* Most/least represented:
	* Artist, Genre
