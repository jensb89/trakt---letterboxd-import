trakt---letterboxd-import
=========================

Import Letterboxd movie list (diary or movie list) into trakt.tv.

## UPDATE (06.2017)
Currently the omdb Api which is used to get the imdb id for each movie has gone private. That means the script will currently fail. A solution is to comment out line 109-116 and set imbd=None afterwards. The omdb Api will probably be free to use again very soon, so I didn't update the code for now.

##Usage:##
1. Export your Letterboxd data (under Settings->Import&Export)
2. Create a trakt.tv application (http://trakt.tv/oauth/applications). Use "urn:ietf:wg:oauth:2.0:oob" as the redirect URI.
3. Fill in the client id, client secret and the code in the python file. The code is obtained by pointing your browser to the Pin-URL.
4a. For diary: $ python py-trakt-letterboxd-import.py diary.csv 
4b. For watched: $ python py-trakt-letterboxd-import.py --watched watched.csv 

Note for the watched.csv: If you choose the watched.csv file every movie marked as watched in letterboxd will be imported. However, since there is no date given at which you have watched the movies (like for the diary), all of them will be imported for the same day and time (time of import) in trakt.tv. 
Furthermore in some rare cases there is no year given/set for some movies in the watched.csv file and therefore the import stops with an error unless you manually set it.


##Thanks##
Some code-parts were taken from https://github.com/akampjes/trakt-list-import !


