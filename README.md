trakt---letterboxd-import
=========================

Import Letterboxd movie list (diary) into trakt.tv

##Usage:##
1. Export your Letterboxd data (under Settings->Import&Export)
2. Create a trakt.tv application (http://trakt.tv/oauth/applications). Use "urn:ietf:wg:oauth:2.0:oob" as the redirect URI.
3. Fill in the client id, client secret and the code in the python file. The code is obtained by pointing your browser to the Pin-URL.
4. $ python py-trakt-letterboxd-import.py diary.csv 

##Thanks##
Some code-parts were taken from https://github.com/akampjes/trakt-list-import !


