#! python3

"""
Scrape lyrics for songs by the band Pavement
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv


def get_song_details(song_dict):
    """
    receives a dictionary containing the song url and title, parses the 
    song page for the album title and lyrics, then returns the completed 
    dictionary containing the full song info
    """

    r = requests.get(song_dict['url'], headers={'User-Agent': 'Custom'})

    if r.status_code != 200:
        print(song_dict['title'] + ': could not find ' + song_dict['url'])
        print('  ' + r.reason)
        song_dict['album'] = ''
        song_dict['lyrics'] = ''

    else:
        soup = BeautifulSoup(r.text, 'lxml')

        # get the album title
        album = soup.find('div', { 'id' : 'song-header-container' })
        try:
            album = album.find_all('a')[1].get('title')[9:]
        except:
            album = 'Unknown'
        song_dict['album'] = album
        
        # get the lyrics
        try:
            lyrics = soup.find(class_='lyricbox')
            lyrics = chr(10).join(lyrics.stripped_strings)
        except:
            lyrics = ''
        song_dict['lyrics'] = lyrics
        
        return song_dict
        

# send the get request for the song list page
main_url = 'http://lyrics.fandom.com/wiki/Category:Songs_by_Pavement'
r = requests.get(main_url, headers={'User-Agent': 'Custom'})

# check that we got a result (should be 200)
if r.status_code != 200:
    print('Could not open the song list at ' + main_url)

else:
    # convert to a soup object and return the text of the result using lxml parser
    soup = BeautifulSoup(r.text, 'lxml')    
    
    # cycle through the list of songs and create a dictionary for each song
    songs = []
    for s in soup.body.find_all(class_="category-page__member-link"):
        song_dict = {}
        song_dict['url'] = 'http://lyrics.fandom.com' + s.get('href')
        song_dict['title'] = s.get('title')[9:]
        songs.append(song_dict)
            
    # iterate through the song list and get the album and lyrics
    for i, song in enumerate(songs):
        songs[i] = get_song_details(song)
    
    # convert to pandas dataframe
    df = pd.DataFrame.from_dict(songs, orient='columns')
    
    # save to a csv file
    df.to_csv('pavement_lyrics.csv', header=True, index=False, \
              encoding='utf-8', quoting=csv.QUOTE_ALL)