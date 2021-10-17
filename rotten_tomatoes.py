import requests
from time import sleep
from bs4 import BeautifulSoup
from requests import TooManyRedirects
import re
import ssl
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from urllib.error import URLError, HTTPError
import json
import csv
from os import path
import pandas as pd

headers = { 'User-Agent':'''
                                    Mozilla/5.0 (X11; Ubuntu;
                                    Linux x86_64;rv:54.0)
                                    Gecko/20100101 Firefox/54.0'''}
ctx = ssl.create_default_context()
baseUrl = 'https://www.rottentomatoes.com/api/private/v2.0/browse?'

def _make_soup(url):
    try:
        r = requests.get(url, headers)
        soup = BeautifulSoup(r.content, 'html.parser')
    except TooManyRedirects:
        soup = ''
    return soup

def _writeMovFile(csv_file, csv_columns,rottenMovies):
    if not path.exists(csv_file):
      with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
          writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
          writer.writeheader()


    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        print(f'Writing to file page {page}')
        for data in rottenMovies:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writerow(data)

def pull_movies(page, service, type, sort):
    rottenMovies = []
    # sort=   tomato  -- release
    # services=   amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now
    # type= dvd-streaming-all --- dvd-streaming-upcoming --- (top-dvd-streaming --- dvd-streaming-new; sort=popularity)
    if page == 1:
        rotten_movies = baseUrl + 'services=' + service + '&type=' + type_search + '&sortby=' + sort
    else:
        rotten_movies = baseUrl + 'services=' + service + '&type=' + type_search + '&sortby=' + sort + '&page=' + str(page)
        
    while True:
        try:
            req = Request(rotten_movies, headers=headers)
            doc = urlopen(req, context=ctx)
        except HTTPError:
            print(f'erroring machin en la page: {page}')
            sleep(10)
            continue
        except ConnectionAbortedError:
            print(f'no interneis: {page}')
            sleep(10)
            continue            
        except KeyboardInterrupt: 
            quit()
        break

    json_movies = doc.read().decode("utf-8")
    y = json.loads(json_movies)
    print(y)
    quit()
    max_movies = y['counts']['count'] - 1
    if max_movies <= 0:
        return []

    for movie in range(0,max_movies):
        y['results'][movie]['audienceScore'] = ''
        y['results'][movie]['criticScore'] = ''
        y['results'][movie]['tomatometerCount'] = ''
        y['results'][movie]['audienceCount'] = ''
        y['results'][movie]['pageNum'] = page
        y['results'][movie]['streamingService'] = service
        
        if not 'synopsis' in y['results'][movie]:
            y['results'][movie]['synopsis'] = ''
        rottenMovie = { useKey: y['results'][movie][useKey] for useKey in csv_columns }
        rottenMovies.append(rottenMovie)
    return rottenMovies

            



if __name__ == "__main__":
    csv_file = 'RottenMovies.csv'
    csv_columns = ['id','pageNum','streamingService','title','url','synopsis', 'mpaaRating','audienceScore','criticScore','audienceCount','tomatometerCount']


#    
    services = ['netflix_iw','amazon%3Bamazon_prime','hbo_go']
    type_search = 'dvd-streaming-all'
    sort = 'tomato'
   
    for service in services:
        page = 1    
        while True:
            rottenMovies = pull_movies(page, service, type_search, sort)
            if not rottenMovies: break
            _writeMovFile(csv_file, csv_columns,rottenMovies)
            page += 1

    df = pd.read_csv(csv_file)
    df.drop_duplicates(subset=['id'], keep='first', inplace=True)
    df.to_csv(csv_file, index=False)
 
 
