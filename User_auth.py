# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:07:35 2021

@author: Ihsaan
"""


import Spotify_Client
import secrets
from flask import Flask, redirect, url_for, session, request
from urllib.parse import urlencode
import requests

#https://github.com/bellerb/Spotify_Flask/blob/master/main.py

CLIENT_ID = "da52de03a4e04567a9e793cad846b349"
client_secret = "95970fa08e2d4df5903a9404790994c0"
secret_key = secrets.token_urlsafe(16)



CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/data".format(CLIENT_SIDE_URL, PORT)

Spotify = Spotify_Client.Spotify_API(CLIENT_ID, client_secret)

#app = Flask(__name__)
#app.secret_key = secret_key


def User_Oauth():
    auth_url, auth_parameters  = Spotify.User_Authorization()
    url_encode = urlencode(auth_parameters)
    user_auth_url ="{}/?{}".format(auth_url, url_encode)
    return user_auth_url

def Access_Refresh_token():
    auth_token = request.args['code']
    access_token_params= { 'grant_type' : 'authorization_code',
                          'code' : str(auth_token),
                          'redirect_uri' : REDIRECT_URI
        }
    headers = Spotify.get_token_header()
    token_url = Spotify.get_token_url()
    
    refresh_access = requests.post(token_url, data = access_token_params, headers = headers)
    response = refresh_access.json()
    
    access_token = response['access_token']
    token_type = response['token_type']
    expires_in = response['expires_in']
    refresh_token = response['refresh_token']
    
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    return authorization_header

def Profile_Data(header):
    # Get user profile data
    user_profile_api_endpoint = Spotify.get_base_url()
    profile_response = requests.get(user_profile_api_endpoint, headers=header)
    profile_data = profile_response.json()
    return profile_data
