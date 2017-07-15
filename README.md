trakt---letterboxd-import
=========================

Import Letterboxd movie list (diary or movie list) into trakt.tv.

## UPDATE (06.2017)
Currently the omdb Api which is used to get the imdb id for each movie has gone private. That means the script will currently fail. A solution is to comment out line 109-116 and set imbd=None afterwards. The omdb Api will probably be free to use again very soon, so I didn't update the code for now.

## Usage:
1. Export your Letterboxd data (under Settings->Import&Export)
2. Create a trakt.tv application (http://trakt.tv/oauth/applications). Use "urn:ietf:wg:oauth:2.0:oob" as the redirect URI.
3. Fill in the client id, client secret and the code in the python file. The code is obtained by pointing your browser to the Pin-URL.
4. (a) For diary: `$ python py-trakt-letterboxd-import.py diary.csv`
4. (b) For watched: `$ python py-trakt-letterboxd-import.py --watched watched.csv`

Note for the watched.csv: If you choose the watched.csv file every movie marked as watched in letterboxd will be imported. However, since there is no date given at which you have watched the movies (like for the diary), all of them will be imported for the same day and time (time of import) in trakt.tv. 
Furthermore in some rare cases there is no year given/set for some movies in the watched.csv file and therefore the import stops with an error unless you manually set it.

### Optional
There is the possibility to optionally use an API for retrieving the imdB id for each movie. This can help if some of the movies have a different title at letterboxd than on imdb or trakt.  However, in most cases this is not needed and the import will take longer when using the API.

If you decide to use it set `CHECK_IMDB_ID = True` and specify an API Url. Typical APIs to use:

1. OmdB Api (was free, currently is [private only](https://www.patreon.com/posts/api-is-going-10743518) and you need to apply for an API key)
2. [TheApache64 API](https://github.com/theapache64/movie_db) A free IMDB Api provided by github User theapache64. An implentation into the trakt-letterboxd importer can be found in this branch: [Click](https://github.com/jensb89/trakt---letterboxd-import/tree/theapache64Api) 

## Thanks
Some code-parts were taken from https://github.com/akampjes/trakt-list-import !


