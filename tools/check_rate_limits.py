import tweepy
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your Twitter API credentials
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

# Authenticate with the Twitter API
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

try:
    # Check rate limit status for various endpoints
    rate_limits = client.get_rate_limit_status()

    print("Rate Limit Status:")
    print("==================")

    # Check specific endpoints we use
    endpoints_to_check = ["/users/me", "/2/users/:id/tweets", "/2/tweets"]

    for endpoint in endpoints_to_check:
        if endpoint in rate_limits.data:
            limit_info = rate_limits.data[endpoint]
            print(f"\nEndpoint: {endpoint}")
            print(f"Remaining: {limit_info['remaining']}")
            print(f"Limit: {limit_info['limit']}")
            print(f"Reset time: {limit_info['reset']}")

except Exception as e:
    print(f"Could not check rate limits: {e}")
    print("\nNote: Rate limit checking might not be available on free plans")
