#!/usr/bin/python

import re
import sys
import urllib2
import json
import getopt
import time
import hashlib
import getpass
import csv
import time
import os.path
import datetime


CLIEN_ID= '' #Fill in your client id
CLIEN_SECRECT = '' #Fill in your client secred
CODE = '' #Fill in your code, which you get after authorization with your trakt account


# Optional: Use an API for obtaining imdb id
CHECK_IMDB_ID = False # Useful for clearly identifying the movie in case the title at letterboxd is dfferent from imdb
API_URL_FOR_IMDB_ID = 'http://www.omdbapi.com/?apikey=YOURAPIKEY&t=' #Fill in your Api key if you want to use omdbapi

def check_authentication():
    if os.path.isfile('auth.json'):
        with open('auth.json') as auth_file:
            auth_data = json.load(auth_file)
            TOKEN = auth_data['access_token']
            REFRESH_TOKEN = auth_data['refresh_token']
            expired = (time.time()-auth_data['created_at']) >=  auth_data['expires_in']

            if expired:
                print 'Authentification expired, trying to re-authentificate...'
                authorize(REFRESH_TOKEN,'refresh')
                return check_authentication()

            return TOKEN

    else:
        print 'Authentication File not found!\n Trying first authentication ...' 
        authorize(CODE)
        return check_authentication()


def authorize(auth_code, grant_type='authorization_code', code=CODE):

    if grant_type == 'authorization_code':

        values = {
            "code": code,
            "client_id": CLIEN_ID,
            "client_secret": CLIEN_SECRECT,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code"
        }

    elif grant_type == 'refresh_token':

        values = {
            "refresh_token": code,
            "client_id": CLIEN_ID,
            "client_secret": CLIEN_SECRECT,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "refresh_token"
        }

    else:
        print 'grant_type has to be authorization_code or refresh_token!!!'

    headers = {
      'Content-Type': 'application/json'
    }
    request = urllib2.Request('https://api-v2launch.trakt.tv/oauth/token', data=json.dumps(values), headers=headers)

    try:
        r = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code == 401:
            print 'CODE maybe wrong / already used?'
            raise Exception("OAuth must be provided")
        elif e.code == 403:
            raise Exception("Invalid API key")
        elif e.code == 400:
            raise Exception("Bad Request - request couldn't be parsed")
        elif e.code == 429:
            raise Exception("Rate Limit Exceeded")
        elif e.code == 500 or e.code == 503 or e.code==520 or e.code==521 or e.code==522:
            raise Exception("Server Error")
    else:
        # 200
        print 'Authentication sucessfull.'
        req = r.read()
        #print req

        print 'Saving authentication token ...'
        f = open('auth.json','w')
        print >> f, req
        f.close()

    #print response_body


def get_data_letterboxd(filename,diary=True):
    #diary true for diary file, false for watched file (no watched date)
    data = []
    with open(filename, 'rb') as csvfile:
        letterboxd_data = csv.reader(csvfile, delimiter=',')
        next(letterboxd_data) #skip header
        for row in letterboxd_data:

            if CHECK_IMDB_ID:
                print 'Get imdbID for ' +  row[1] + '(' + row[2] + ')'
                imdbinfo = get_imdb_info(row[1], year=int(row[2]))
                print imdbinfo
                if imdbinfo['Response'] != 'False':
                    print "Success!"
                else:
                    print "Failed! IMDB ID was not found. Try to add movie to trakt w/o ID."
                imdbid = imdbinfo.get('imdbID',None)
            else:
                imdbid = None

            if diary:
                data.append([row[1],row[2],row[7]+' 20:15',imdbid])
                print [row[1],row[2],row[7]+' 20:15',imdbid]
            else:
                data.append([row[1],row[2],'released',imdbid])
                print [row[1],row[2],'released',imdbid]
            time.sleep(0.2)

    return data

def send_data(movie_data, auth_token):
    #movie_data = [{'imdb_id':imdb_id,'title':title,'year':year,'last_played': date_played}]
    pydata = {
            'movies': movie_data
            }
    json_data = json.dumps(pydata)
    clen = len(json_data)

    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + auth_token,
    'trakt-api-version': '2',
    'trakt-api-key': CLIEN_ID
    }
    req = urllib2.Request('https://api-v2launch.trakt.tv/sync/history', data=json_data, headers=headers)

    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    f = open('log.txt','a')
    print >> f, response
    f.close()

def get_imdb_info(title, year=None):
    if year != None:
        s=API_URL_FOR_IMDB_ID+title+'&y='+str(year)
    else:
        s=API_URL_FOR_IMDB_ID+title
    url = urllib2.urlopen(s.replace(' ','%20'))
    data = url.read()
    res = json.loads(data)
    return res

def usage(argv0):
    print('usage: '+argv0+' [OPTION] FILE ...')
    print('''
    OPTIONS
    -h
    --help          Show help
    --watched       Use watched.csv file instead of diary (no watched date!!)
    --debug         Turn on debuging mode (doesn't exist)
    EXAMPLE USAGE
        python py-trakt-letterboxd-import.py diary.csv
    ''')
    sys.exit(1)

if __name__ == "__main__":
    use_diary_file = True
    try:
        args, letterboxd_file = getopt.gnu_getopt(sys.argv[1:], 'h:w',[
            'help','watched'])
    except:
        print "\nPlease  c h e c k   a r g u m e n t s\n\n"
        usage(sys.argv[0])

    for opt, arg in args:
        if opt in ['--help', '-h']:
            usage(sys.argv[0])
        elif opt == '--watched':
            use_diary_file = False 
        else:
            print('unknown option '+opt)
            usage(sys.argv[0])

    print 'Authentication with Trakt.tv....'
    token = check_authentication()

    print letterboxd_file[0]
    data = get_data_letterboxd(letterboxd_file[0],use_diary_file)

    print str(len(data)) + 'movies in file.' 
    movie_data = [];
    skipped = [];

    for line in data:
        title = line[0]
        year = line[1]
        date_played = line[2]
        imdbid = line[3]
        #print date_played
        #print time.strftime(date_played, '%Y-%m-%d %H:%M')
        if not year: #if for some reason a year information is not available the entry is skipped
            skipped.append(title)
        else:
            movie_data.append({'title':title,'year':int(year),'watched_at': date_played,'ids':{'imdb_id':imdbid}})

        # send batch of 100 IMDB IDs
        if len(movie_data) >= 100:
            print 'Importing first 100 movies...'
            send_data(movie_data,auth_token=token)
            movie_data = []

    if len(movie_data) > 0:
        send_data(movie_data,auth_token=token)

    if len(skipped) > 0:
        print str(len(skipped)) + ' movie(s) skipped due to missing year information:'
        print skipped
