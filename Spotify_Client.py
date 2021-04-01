#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import numpy
import pandas
import os
import base64
import certifi
import datetime
from urllib.parse import urlencode
import os
from flask import Flask, request
# 
# Authentication: I prove who I say I am -> username & password
# 
# Authorization: I prove that someone else told me I could acess something -> Oauth
# 

# In[2]:


#client_id = os.environ['Spotify_Client_ID']
#client_secret = os.environ['Spotify_Client_Secret']

CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000

class Spotify_API(object):
    
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    api_version = 'v1'
    base_url = 'https://api.spotify.com/{}'.format(api_version)
    auth_url ='https://accounts.spotify.com/authorize'
    REDIRECT_URI = "{}:{}/data".format(CLIENT_SIDE_URL, PORT) #ensure the url is the same as iu the spotify dashboard app

    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs) #if you want inherit for request 
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_token_url(self):
        return self.token_url
    
    def get_base_url(self):
        return self.base_url
    
# =============================================================================
#     AUTHORIZATION & AUTHENTICATION
# =============================================================================
    
    def get_client_credentials(self):
        """
        returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        
        if client_id == None or client_secret == None:
            raise Exception('Client Id and Secret not set')
            
        #need to encode to base 64 sting as per spotify docs
        client_creds_b64 = base64.b64encode("{}:{}".format(client_id,client_secret).encode())
        return client_creds_b64.decode()

    def get_token_header(self):
        #header for minimal auth access(no user data)
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": "Basic {}".format(client_creds_b64)} #authorization header as per docs
    
    def get_token_data(self):
        return {'grant_type' : 'client_credentials'}
    
    def perform_authorization(self):
        print('Authorization')
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()
        
        req = requests.post(token_url, data = token_data, headers = token_headers)
        
        if req.status_code not in range(200,299):
            raise Exception('Could not authentiacate client')
        
        data = req.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in'] #in seconds
        expires = now + datetime.timedelta(seconds=expires_in) #needed for new token
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now

        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        #print(token)
        
        if expires < now:
            #authentitacation expired, redo authentication
            self.perform_authorization()

            return self.get_access_token()
        
        elif token == None:
            self.perform_authorization()
            return self.get_access_token()
            
        return token
    
    def get_access_headers(self):
        access_token = self.get_access_token()
        header = {'Authorization': "Bearer {}".format(access_token)}  #header as per doc
        return header 
    
    #TO ACCESS USER DATA
    
    def User_Authentication(self):
        auth_url = self.auth_url
        app_scopes = 'user-top-read playlist-modify-private user-follow-read user-library-read'
        #redirect uri is unique to each dev's dashboard
        header = { 'client_id' : self.client_id,
                 'response_type' : 'code',
                 'redirect_uri' : self.REDIRECT_URI,
                 'scope' : app_scopes}
        return auth_url, header
    
    def User_Oauth(self):
        #get user to approve accessing data, need to redirect user to this url
        auth_url, auth_parameters  = self.User_Authentication()
        url_encoded = urlencode(auth_parameters)
        user_auth_url ="{}/?{}".format(auth_url, url_encoded)
        return user_auth_url

    def Access_Refresh_token(self):
        #confirm authorization and request for a refresh token from spotify
        auth_token = request.args['code']
        access_token_params= { 'grant_type' : 'authorization_code',
                              'code' : str(auth_token),
                              'redirect_uri' : self.REDIRECT_URI}
        headers = self.get_token_header()
        token_url = self.get_token_url()
        
        refresh_access = requests.post(token_url, data = access_token_params, headers = headers)
        
        if refresh_access.status_code not in range(200,299):
            raise Exception('Could not Authorize User')
        
        response = refresh_access.json()
        
        
        access_token = response['access_token']
        token_type = response['token_type']
        expires_in = response['expires_in']
        refresh_token = response['refresh_token']
        
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=expires_in)
        
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        
        #authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        return True
    
       
# =============================================================================
#    SIMPLE SEARCH, USER OAUTH NOT NEEDED ONLY BASIC SPOTIFY CLIENT AND SECRET 
# =============================================================================
    
    def get_ressources(self, lookup_id, ressource_type = 'artists'): #generalization to implement multiple gets
        ''''
        Parameters
        ----------
        lookup_id : Int
            DESCRIPTION.
            
        ressource_type : String, optional
            DESCRIPTION. The default is 'track'. Other option is 'artist'

        Returns
        -------
        TYPE
            DESCRIPTION. Json of lookup results
        '''
        #want to modify so it can handle multiple inputs...
        endpoint = "{}/{}/{}".format(self.base_url,ressource_type,lookup_id)
        headers = self.get_access_headers()
        req = requests.get(endpoint, headers = headers)
        #print(req)
        if req.status_code not in range(200,299):
            return {}
        return req.json()
    
    
    def get_album(self, album_id):
        return self.get_ressources(album_id, ressource_type = 'albums')
    
    def get_artist(self, artist_id):
        return self.get_ressources(artist_id, ressource_type = 'artists')
    
    def get_track(self, track_id):
        return self.get_ressources(track_id, ressource_type = 'track')
    
    
    def base_search(self, query_params, search_type='track'):
        '''
        Parameters
        ----------
        query_params : TYPE -> #url ready string (ex using urlencode())
            DESCRIPTION.
            
        search_type : TYPE, optional
            DESCRIPTION. The default is 'track'. Other option is 'artist'

        Returns
        -------
        TYPE
            DESCRIPTION. Json of search results

        '''
        
        header = self.get_access_headers()
        endpoint = "{}/search".format(self.base_url) #get
        search_url = "{}?{}".format(endpoint,query_params)
        #print(search_url)
        
        req = requests.get(search_url, headers = header)
        if req.status_code not in range(200,299):
            return {}
        return req.json()

    def search(self, query = None, operator = None, operator_query = None, search_type = 'artist'):
        '''
        Parameters
        ----------
        query : String
            DESCRIPTION. The default is None. Can consist simply of a name of song or artists.
            Can be complex to include song name and artist
            
        operator : String, optional
            DESCRIPTION. The default is None. NOT, AND, OR
            
        operator_query : String, optional
            DESCRIPTION. The default is None. What is subsequent to the Operator ie NOT Metalica
            
        search_type : String, optional
            DESCRIPTION. The default is 'artist'. Other option is'track'

        Raises
        ------
        Exception
            DESCRIPTION. If a query is not inputed

        Returns
        -------
        TYPE
            DESCRIPTION. Json data of the search result.
            
            
        EXAMPLES
        --------
        search for queries and operators(not, and, or)
        spotify.search(query = 'Hangman', search_type = 'track')
        spotify.search({'track' : 'Hangman', 'artist': "Dave"}, search_type = 'track')
        spotify.search(query= 'Hangman', operator ='not', operator_query='Tom', search_type = 'track')

        '''
        ###NEED TO HANDLE AND CLEAN DATA
       
        if query == None:
            raise Exception('A query is required')
        
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])#converting dict to list
            
        if operator != None and operator_query != None:
            operator = operator.upper()
            if operator == 'OR' or operator == 'NOT':
                if isinstance(operator_query, str):
                    query = "{} {} {}".format(query,operator,operator_query)
            
        query_params = urlencode({"q": query, "type":search_type.lower()}) #url ready string
        #print(query_params)
        
        return self.base_search(query_params)
    
    def get_related_artists(self, artist_id):
        '''
        the response body contains an object whose key is "artists" and whose value is an array of up to 20 artist objects in JSON format. 
        '''        
        r_artist_end ='{}/artists/{}/related-artists'.format(self.get_base_url(),artist_id)
        headers = self.get_access_headers()
        r_artists = requests.get(r_artist_end, headers = headers)
        r_artists_data = r_artists.json()
        return r_artists_data
        
    
# =============================================================================
#     USER DATA APIs, Authentication NEEDED!
# =============================================================================
    
    def Profile_Data(self):
        # Get user profile data
        user_profile_api_endpoint = '{}/me'.format(self.get_base_url())
        headers = self.get_access_headers()
        profile_response = requests.get(user_profile_api_endpoint, headers=headers)
        profile_data = profile_response.json()
        return profile_data
        
    def get_User_Top_Data(self, datatype = "tracks", time_range = 'medium_term', limit = 50, offset= 0):
        '''
        Parameters
        ----------
        type : String, optional
            DESCRIPTION. The default is "tracks". Other option is 'artists'
            
        time_range : String, optional
            DESCRIPTION. The default is 'medium_term' = last 6 months, 'long_term' = serveral years, "short_term" -> last 4 wwks
        
        limit : TYPE, optional
            DESCRIPTION. The default is 50., maximum is 50, the number of entities returned.
        
        offset : TYPE, optional
            DESCRIPTION. The default is 0. The index of the first entry, used to obtain different sets of data

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        #	https://api.spotify.com/v1/me/top/{type}
        query_params = urlencode({"time_range": time_range, "limit":limit, "offset":offset})
        top_api_endpoint = '{}/me/top/{}?{}'.format(self.get_base_url(), datatype, query_params)
        print(top_api_endpoint)
        headers = self.get_access_headers()
        top_data = requests.get(top_api_endpoint, headers=headers)
        top_data = top_data.json()
        return top_data
    
    '''
    API Endpoints to look at

    -> get recommendations
    -> personalization api -> get top tracks and artists
    -> Tracks API for  get audio features.
    
    '''


#spotify = Spotify_API(client_id, client_secret)











