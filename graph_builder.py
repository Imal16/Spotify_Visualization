# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 17:38:17 2021

@author: Ihsaan
"""
from collections import defaultdict
import os
from pyvis.network import Network
#https://pyvis.readthedocs.io/en/latest/documentation.html
import Spotify_Client


CLIENT_ID = os.environ['Spotify_Client_ID']
CLIENT_SECRET = os.environ['Spotify_Client_Secret']
Spotify = Spotify_Client.Spotify_API(CLIENT_ID, CLIENT_SECRET)


def get_genres(genres_list):
    #get genre, need to find a better way to classify
    domain = ['hip hop','grime', 'edm', 'pop', 'country', 'jazz','rock','classical','r&b','metal','rap']
    dominant = set(domain)
    
    flag = 0
    temp = None
    artist_genre = None
    for genre in genres_list:
        if genre in dominant and flag != 1:
            artist_genre = genre
            flag = 1
            break
        else:
            if flag == 0:
                temp = genre
                flag = -1
                
    if flag == -1:
        #edges cases, need better way to
        if temp == "pop dance":
            temp = 'edm'
        elif temp == 'sad rap':
            temp = 'emo rap'
        elif temp == 'indie hip hop':
            temp = 'hip hop'
        artist_genre = temp
        
    return artist_genre

def build_graph(user_data = False, max_related = None):
    
    artist_graph = defaultdict(dict)
    
    if user_data:
        
        user_top = Spotify.get_User_Top_Data('artists','long_term')
        
        for items in user_top['items']:
            
            artist_genre = get_genres(items['genres'])
            artist_graph[items['name']] = {'related': [], 'id': items['id'], 'genre': artist_genre,
                                           'image': items['images'][0]['url'],
                                           'followers': items['followers']['total'],
                                           'popularity': items['popularity'], 'Top' : True}

    else:
        
        top_ids = ['5K4W6rqBFWDnAN6FQUkS6x', '3TVXtAsR1Inumwj472S9r4', '2SrSdSvpminqmStGELCSNd', '6nxWCVXbOlEVRexSbLsTer', '60d24wfXkVzDSfLS6hyCjZ', '6Ip8FS7vWT1uKkJSweANQK', '50JJSqHUf2RQ9xsHs0KMHg', '02kJSzxNuaWGqwubyUba0Z', '1Bl6wpkWCQ4KVgnASpvzzA', '3hOdow4ZPmrby7Q1wfPLEy', '2cFrymmkijnjDg9SS92EPM', '6l3HvQ5sa6mXTsMTB19rO5', '1vCWHaC5f2uS3yhpwWbIA6', '0c173mlxpT3dSFRgMO8XPh', '246dkjvS1zLTtiykXe5h60', '5f7VJjfbwm532GiveGC0ZK', '4Xi6LSfFqv26XgP9NKN26U', '0EeQBlQJFiAfJeVN2vT9s0', '4Dokdwa3WB7ilQ2c2qvIBL', '3nFkdlSjzX9mRTtwJOzDYB', '2qxJFvFYMEDqd7ui6kSAcq', '2ZeAzgQtLfcPmMap31S0dZ', '6USv9qhCn6zfxlBQIYJ9qs', '20sxb77xiYeusSH8cVdatc', '3gIRvgZssIb9aiirIg0nI3', '5Matrg5du62bXwer29cU5T', '0huGjMyP507tBCARyzSkrv', '1gPhS1zisyXr5dHTYZyiMe', '0Y5tJX1MQlPlqiwlOH1tJY', '7fqDRFkiuwzFDde1K0taVs', '2P5sC9cVZDToPxyomzF1UH', '6eUKZXaKkcviH0Ku9w2n3V', '15UsOTVnJzReFVN1VCnxy4', '0gusqTJKxtU1UTmNRMHZcv', '5zctI4wO9XSKS8XwcnqEHk', '3IYUhFvPQItj6xySrBmZkd', '3eqjTLE0HfPfh78zjh6TqT', '4IZLJdhHCqAvT4pjn8TLH5', '67ea9eGLXYMsO2eYQRui3w', '2jku7tDXc6XoB6MO2hFuqg', '7FqkRutc4zWMrnEAUv3Xwd', '039zhJoEkboZ8Ii6K40Fb6']
        
        for a_id in top_ids:
            
            artist_data = Spotify.get_artist(a_id)
            artist_genre = get_genres(artist_data['genres'])
            artist_graph[artist_data['name']] = {'related': [], 'id': artist_data['id'], 
                                    'genre': artist_genre, 'image': artist_data['images'][0]['url'],
                                    'followers': artist_data['followers']['total'],
                                     'popularity': artist_data['popularity'],'Top' : True}
            
    temp_graph = artist_graph.copy()

    for i in temp_graph:
        
        print('Building Relations for: ', i)
        related = Spotify.get_related_artists(artist_graph[i]['id'])
        counter = 0
        
        for related_artist in related['artists']:
            
            if counter == max_related:
                break ##exit loop no more related requested
            
            if related_artist['name'] in artist_graph:
                artist_graph[i]['related'].append(related_artist['name'])
                artist_graph[related_artist['name']]['related'].append(i)
                
            else:
                
                artist_genre = get_genres(related_artist['genres'])
                artist_graph[i]['related'].append(related_artist['name'])
                artist_graph[related_artist['name']] = {'related': [i], 'id': related_artist['id'],
                                    'genre': artist_genre, 'image': related_artist['images'][0]['url'],
                                    'followers': related_artist['followers']['total'],
                                     'popularity': related_artist['popularity'],'Top': False}
            counter += 1
                    
    return artist_graph


def visualize_graph(graph):
    Artist_Network = Network(height='100%',width='100%')
    
    for artist in graph:
        #print('Adding Top Artist: ', artist)
        try:
            Artist_Network.get_node(artist)
            
        except:
            print('Adding Top Artist: ', artist)
            title = "{}, User's Top Artist, Genre: {}".format(artist, graph[artist]['genre'])
            
            Artist_Network.add_node(artist, label = artist, group = graph[artist]['genre'],
                                    shape = 'circularImage', image = graph[artist]['image'],
                                    borderWidth = 3, size = int(graph[artist]['popularity'])/2,
                                    labelHighlightBold = True, title = title,
                                    physics = True)
            #value = int(graph[artist]['followers']),
            
        for related in graph[artist]['related']:
            
            try:
                #print('Adding Related Artist: ', artist)
                Artist_Network.get_node(related)
    
            except:
                print('Adding Related Artist: ', related)
                title = "{}, Genre: {}".format(related, graph[artist]['genre'])
                
                Artist_Network.add_node(related, label = related, group = graph[related]['genre'], 
                                   shape = 'circularImage', image = graph[related]['image'],
                                   borderWidth = 1.5,
                                   size = int(graph[artist]['popularity'])/2,
                                   title = title,
                                   physics = True)
                # value = int(graph[related]['followers']),
                
            Artist_Network.add_edge(artist,related, physics = True)
    
    print('Outputting Graph...')
    Artist_Network.show('example.html')
    
    return Artist_Network


#IF want to improve, compare audio features to get discrimanating features to color of edges
#map map differentiating audio features to a color via dict and then forllow something like
#https://stackoverflow.com/questions/63717126/how-to-change-the-color-of-subgraph-using-pyvis

