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



def _make_soup(url):
    '''
    Create BeautifulSoup instance for the webpage of the request.
    url: string for webpage
    '''
    try:
        r = requests.get(url, headers)
        soup = BeautifulSoup(r.content, 'html.parser')
    except TooManyRedirects:
        soup = ''
    return soup

def _writeMovFile(csv_file, csv_columns,rottenMovies):
    '''
    Creates file with parsed data
    csv_file: Name of the file
    csv_columns: Names for the columns to be parsed
    rottenMovies: Dictionary with data parsed
    '''
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
    '''
    Gets movies in a given page using rotten tomatoes api
    page: int, number of the page to get movies
    service: Service fiter (netflix to prime) amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now
    type: filter for type of movie getting "dvd-streaming-all - dvd-streaming-upcoming - top-dvd-streaming - dvd-streaming-new" 
    sort: tomato (better critic review) -- release (by release date)
    '''
    baseUrl = 'https://www.rottentomatoes.com/api/private/v2.0/browse?'
    ctx = ssl.create_default_context()
    rottenMovies = []
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
    max_movies = y['counts']['count'] - 1
    if max_movies <= 0:
        return []

    for movie in range(0,max_movies):
        y['results'][movie]['audienceScore'] = ''
        y['results'][movie]['criticScore'] = ''
        y['results'][movie]['tomatometerCount'] = ''
        y['results'][movie]['audienceCount'] = ''
        y['results'][movie]['rating'] = ''
        y['results'][movie]['info'] = ''
        
        y['results'][movie]['pageNum'] = page
        y['results'][movie]['streamingService'] = service
        
        if not 'synopsis' in y['results'][movie]:
            y['results'][movie]['synopsis'] = ''
        rottenMovie = { useKey: y['results'][movie][useKey] for useKey in csv_columns }
        rottenMovies.append(rottenMovie)
    return rottenMovies

def _print_welcome():
    print ('-='*30  )
    print ('What ya want?')
    print ('[C]reate movie file\n')
    print ('[U]pdate details\n')
    print ('-='*30  )

def _get_movie_info(movie):
    '''
    Get info about a movie by parsing script that fills template page
    void funtion
    movie: Movie URL to parse
    '''
    soup = _make_soup('https://www.rottentomatoes.com/'+movie[1])
    section = soup.find("script", attrs ={'id' : "score-details-json"}).string
    y = json.loads(section)
    audienceScore = y['scoreboard']['audienceScore'] or 0
    tomatometerScore = y['scoreboard']['tomatometerScore']
    audienceCount = y['scoreboard']['audienceCount']
    tomatometerCount = y['scoreboard']['tomatometerCount']
    rating = y['scoreboard']['rating']
    info = y['scoreboard']['info']
    df.loc[df.id == int(movie[0]),'audienceScore'] = y['scoreboard']['audienceScore']
    df.loc[df.id == int(movie[0]),'criticScore'] = y['scoreboard']['tomatometerScore']
    df.loc[df.id == int(movie[0]),'audienceCount'] = y['scoreboard']['audienceCount']
    df.loc[df.id == int(movie[0]),'tomatometerCount'] = y['scoreboard']['tomatometerCount']
    df.loc[df.id == int(movie[0]),'rating'] = y['scoreboard']['rating']
    df.loc[df.id == int(movie[0]),'info'] = y['scoreboard']['info']

if __name__ == "__main__":
    _print_welcome()

    csv_file = 'RottenMovies.csv'
    csv_columns = ['id','pageNum','streamingService','title','url','synopsis', 'rating','audienceScore','criticScore','audienceCount','tomatometerCount','info']
    services = ['netflix_iw','amazon%3Bamazon_prime','hbo_go']
    type_search = 'dvd-streaming-all'
    sort = 'tomato'

    command = input().upper()

    if command == 'C':
        for service in services:
            page = 1    
            while True:
                rottenMovies = pull_movies(page, service, type_search, sort)
                if not rottenMovies: break
                _writeMovFile(csv_file, csv_columns,rottenMovies)
                page += 1
    elif command == 'U':
        df = pd.read_csv(csv_file)
        df.drop_duplicates(subset=['id'], keep='first', inplace=True)
        df.to_csv(csv_file, index=False)

        with open(csv_file, 'r', encoding='utf-8') as rotten_movies:
            csvreader = csv.reader(rotten_movies)
            header = next(csvreader)
            movies = [ (movie[0], movie[4]) for  movie in csvreader]

        i = 0
        removedMovies = 0
        for movie in movies:
            i += 1

            loop_continue = df.loc[df.id==int(movie[0]), 'audienceCount'].isna().values[0]
            audienceCount = df.loc[df.id==int(movie[0]), 'audienceCount']
            if not loop_continue:
                print(f'{movie[1]} has {audienceCount.values[0]} audience ratings \n')
                continue
            print(f'{i} ---- {movie[1]}')

            try:
                _get_movie_info(movie)
            except requests.exceptions.ConnectionError:
                print(f'no interneis: {movie}')
                sleep(25)
                continue             
            except AttributeError:
                # df.drop([int(movie[0])], inplace = True) 
                removedMovies += 1
                print(f'Movie 404 -- {removedMovies}')
        
                df.drop( df[df['id'] == int(movie[0])].index, inplace = True) 
            except KeyboardInterrupt:  
                saveMovies = input(f'Save File? -- removedMovies =  {removedMovies}\n (y:yes any other: no): ')  
                if saveMovies == 'y':
                    df.to_csv(csv_file, index=False)
                    quit()
                else:
                    quit()
            except Exception as e:
                print('Error culeysote ',e)
                saveMovies = input(f'Save File? -- removedMovies =  {removedMovies}\n (y:yes any other: no): ')  
                if saveMovies == 'y':
                    df.to_csv(csv_file, index=False)
                    quit()
                else:
                    quit()
