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

# 
# Authentication: I prove who I say I am -> username & password
# 
# Authorization: I prove that someone else told me I could acess something -> Oauth
# 

# In[2]:


#client_id = os.environ['Spotify_Client_ID']
#client_secret = os.environ['Spotify_Client_Secret']




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
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs) #if you want inherit for request 
        self.client_id = client_id
        self.client_secret = client_secret
    
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
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": "Basic {}".format(client_creds_b64)}
    
    def get_token_data(self):
        return {'grant_type' : 'client_credentials'}
    
    def perform_authentication(self):
        print('Authentication')
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
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now

        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        print(token)
        
        if expires < now:
            #authentitacation expired, redo
            self.perform_authentication()

            return self.get_access_token()
        
        elif token == None:
            self.perform_authentication()
            return self.get_access_token()
            
        return token
    
    def User_Authorization(self):
        auth_url = self.auth_url
        app_scopes = 'user-top-read playlist-modify-private user-follow-read user-library-read'
        header = { 'client_id' : self.client_id,
                 'response_type' : 'code',
                 'redirect_uri' : 'http://127.0.0.1:5000/data',
                 'scope' : app_scopes}
        return auth_url, header
    
    def get_token_url(self):
        return self.token_url
    
    def get_base_url(self):
        return self.base_url
    
    
    
    def get_ressources_headers(self):
        access_token = self.get_access_token()
        header = {'Authorization': "Bearer {}".format(access_token)}
        return header
    
    def get_ressources(self, lookup_id, ressource_type = 'artists'):
        endpoint = "{}/{}/{}".format(self.base_url,ressource_type,lookup_id)
        headers = self.get_ressources_headers()
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
        
        header = self.get_ressources_headers()
        endpoint = "{}/search".format(self.base_url) #get
        search_url = "{}?{}".format(endpoint,query_params)
        print(search_url)
        
        req = requests.get(search_url, headers = header)
        if req.status_code not in range(200,299):
            return {}
        return req.json()

    def search(self, query = None, operator = None, operator_query = None, search_type = 'artist'):
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


#spotify = Spotify_API(client_id, client_secret)




#spotify.search(query = 'Hangman', search_type = 'track')



#spotify.search({'track' : 'Hangman', 'artist': "Dave"}, search_type = 'track')



#spotify.search(query= 'Hangman', operator ='not', operator_query='Tom', search_type = 'track')






