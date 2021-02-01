# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 18:28:14 2021

@author: Ihsaan
"""

from flask import Flask, request, redirect
from User_auth import User_Oauth, Access_Refresh_token, Profile_Data
import secrets

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
app.secret_key = secret_key

@app.route("/")
def index():
    # Authorization
    auth_url = User_Oauth()
    return redirect(auth_url)

@app.route("/data")
def callback():
    print('callback')
    authorization_header = Access_Refresh_token()

    #Gathering of profile data
    print('profile_data')
    profile_data = Profile_Data(authorization_header)
    print(profile_data)
    
    return profile_data
    


if __name__ == "__main__":
    app.run()