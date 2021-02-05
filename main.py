# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 18:28:14 2021

@author: Ihsaan
"""

from flask import Flask, request, redirect
import secrets
import os
import Spotify_Client


CLIENT_ID = os.environ['Spotify_Client_ID']
CLIENT_SECRET = os.environ['Spotify_Client_Secret']

Spotify = Spotify_Client.Spotify_API(CLIENT_ID, CLIENT_SECRET)

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
app.secret_key = secret_key

@app.route("/")
def index():
    # Authorization
    auth_url = Spotify.User_Oauth()
    return redirect(auth_url)

@app.route("/data")
def callback():
    print('callback')
    Spotify.Access_Refresh_token()

    #Gathering of profile data
    print('profile_data')
    profile_data = Spotify.Profile_Data()
    print(profile_data)
    
    return profile_data
    


if __name__ == "__main__":
    app.run()