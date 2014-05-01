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


USERNAME = ''
PASSWORD = ''
APIKEY = ''
PASSWORD = hashlib.sha1(PASSWORD).hexdigest()


def get_data_letterboxd_diary(filename):
    data = []
    with open(filename, 'rb') as csvfile:
        diary = csv.reader(csvfile, delimiter=',')
        next(diary) #skip header
        for row in diary:
            print 'Get imdbID for ' +  row[1] + '(' + row[2] + ')'
            imdbinfo = get_imdb_info(row[1], year=int(row[2]))
            #print imdbinfo
            if imdbinfo['Response'] != 'False':
                print "Success!"
            else:
                print "Failed! IMDB ID was not found. Try to add movie to trakt w/o ID."

            imdbid = imdbinfo.get('imdbID',None)
            data.append([row[1],row[2],row[6]+' 20:15',imdbid])
            time.sleep(0.2)

    return data

def send_data(movie_data):
    #movie_data = [{'imdb_id':imdb_id,'title':title,'year':year,'last_played': date_played}]
    pydata = {
            'username':USERNAME,
            'password':PASSWORD,
            'movies': movie_data
            }
    json_data = json.dumps(pydata)
    clen = len(json_data)
    #print json_data
    #f = open('sample.json', 'w')
    #print >> f, json_data
    #f.close()
    req = urllib2.Request("https://api.trakt.tv/movie/seen/"+APIKEY, json_data, {'Content-Type': 'application/json', 'Content-Length': clen})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    f = open('log.txt','a')
    print >> f, response
    f.close()

def get_imdb_info(title, year=None):
    if year != None:
        s='http://omdbapi.com/?t='+title+'&y='+str(year)
    else:
        s='http://omdbapi.com/?t='+title
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
    --username=     Your username
    --password=     Your password (not recommended, instead enter password when prompted)
    --apikey=       Your API key (get from here: http://trakt.tv/api-docs/authentication)
    --debug         Turn on debuging mode (doesn't exist)

    EXAMPLE USAGE
        python py-trakt-letterboxd-import.py diary.csv
    ''')
    sys.exit(1)

if __name__ == "__main__":
    try:
        args, letterboxd_file = getopt.gnu_getopt(sys.argv[1:], 'h',[
            'help','username=','password=','apikey='])
    except:
        print "\nPlease  c h e c k   a r g u m e n t s\n\n"
        usage(sys.argv[0])

    for opt, arg in args:
        if opt in ['--help', '-h']:
            usage(sys.argv[0])
        elif opt in ['--username']:
            USERNAME = arg
        elif opt in ['--password']:
            PASSWORD = hashlib.sha1(arg).hexdigest()
        elif opt in ['--apikey']:
            APIKEY = arg
        else:
            print('unknown option '+opt)
            usage(sys.argv[0])

    if USERNAME == '':
        USERNAME = raw_input("enter trakt username: ")
    if APIKEY == '':
        APIKEY = raw_input("enter trakt apikey: ")
    if PASSWORD == '':
        PASSWORD = hashlib.sha1(getpass.getpass("enter trakt password (input hidden):")).hexdigest()

    print letterboxd_file[0]
    data = get_data_letterboxd_diary(letterboxd_file[0])
    print str(len(data)) + 'movies in file.' 
    movie_data = [];

    for line in data:
        title = line[0]
        year = line[1]
        date_played = line[2]
        imdbid = line[3]
        movie_data.append({'imdb_id':imdbid,'title':title,'year':int(year),'last_played': int(time.mktime(time.strptime(date_played, '%Y-%m-%d %H:%M')))})

        # send batch of 100 IMDB IDs
        if len(movie_data) >= 100:
            print 'Importing first 100 movies...'
            send_data(movie_data)
            movie_data = []

    if len(movie_data) > 0:
            send_data(movie_data)