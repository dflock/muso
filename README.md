# muso

Music Collection Auditor

This script will do the following things, eventually:

## Assume the following folder structures:

	~/Music/artist/album/
	~/Music/Compilations/album/
	~/Music/Soundtracks/album/
	~/Music/Classical/album/ ?

Report folders that don't match.

## Check for:

* Albums with any of the following tags not the same for each track:
	* album, albumartist, discnumber, genre, date
	* replaygain_album_gain, replaygain_album_peak
	* musicbrainz_albumid, musicbrainz_albumartistid

* Tracks missing any of the following tags:
	* album, artist, albumartist, tracknumber, discnumber, title, genre, date
	* replaygain_album_gain, replaygain_album_peak, replaygain_track_gain, replaygain_track_peak
	* musicbrainz_albumid, musicbrainz_albumartistid, musicbrainz_trackid

* A folder.jpeg|jpg in each album & artist folder, of at least 500x500px
* Extraneous .m3u, .info, .sfv, etc... files.