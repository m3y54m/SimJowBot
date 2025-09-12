# This script helps you get the access token and access token secret
# for your Twitter developer account using 3-legged OAuth.
# it is not part of the bot, just a helper script.

import os
from dotenv import load_dotenv
import tweepy

# take environment variables from .env.
load_dotenv()

# get environment variables for Twitter API
consumer_key = os.environ.get("API_KEY")
consumer_secret = os.environ.get("API_KEY_SECRET")

# 3-legged OAuth
auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback="oob")
auth.secure = True
auth_url = auth.get_authorization_url()

# Open the link while signed in your desired bot account
print("Please authorize: " + auth_url)

# Get the 7-digit PIN code generated from the url
verifier = input("PIN: ").strip()

auth.get_access_token(verifier)

print('ACCESS_TOKEN="%s"' % auth.access_token)
print('ACCESS_TOKEN_SECRET="%s"' % auth.access_token_secret)
