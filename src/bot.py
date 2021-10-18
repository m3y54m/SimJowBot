import os
import time
from datetime import datetime
import tweepy
from dotenv import load_dotenv

# take environment variables from .env.
load_dotenv()

# get environment variables for Twitter API
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")


def twitter_api_authenticate():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    try:
        api.verify_credentials()
    except Exception as error:
        print(
            f"\n[ SimJowBot ] An error occurred while attempting to authenticate with the twitter API. Reason:\n{error}"
        )
        return None
    else:
        return api


def get_tweet(twitterApi, tweetId):
    userName = None
    tweetText = None

    if twitterApi:
        try:
            status = twitterApi.get_status(id=tweetId)
        except Exception as error:
            print(
                f"\n[ SimJowBot ] An error occurred while attempting to get the twitter status with id={tweetId}. Reason:\n{error}"
            )
        else:
            userName = status.user.name
            tweetText = status.text

    return userName, tweetText


def post_tweet(twitterApi, tweetText):
    success = False

    if twitterApi:
        try:
            twitterApi.update_status(status=tweetText)
        except Exception as error:
            print(
                f"\n[ SimJowBot ] An error occurred while attempting to update the twitter status. Reason:\n{error}"
            )
        else:
            success = True

    return success


class SimJowStream(tweepy.Stream):
    def __init__(
        self, consumer_key, consumer_secret, access_token, access_token_secret
    ):
        super().__init__(
            consumer_key, consumer_secret, access_token, access_token_secret
        )

        self.twitterApi = twitter_api_authenticate()
        self.myUser = self.twitterApi.get_user(screen_name="SimJow")

    # when a new tweet is posted on Twitter with your filtered specifications
    def on_status(self, status):
        # If the user is not myself
        if status.user.screen_name != self.myUser.screen_name:

            print(f"\n[ SimJowBot ] Found tweet with id={status.id} by @{status.user.screen_name}.")

            try:
                # Like the tweet
                self.twitterApi.create_favorite(status.id)
            # Some basic error handling. Will print out why retweet failed, into your terminal.
            except Exception as error:
                print(
                    f"\n[ SimJowBot ] ERROR: Favorite not successful. Reason:\n{error}"
                )
            else:
                print(f"\n[ SimJowBot ] Favorite published successfully.")

            try:
                # Retweet the tweet
                self.twitterApi.retweet(status.id)
            # Some basic error handling. Will print out why retweet failed, into your terminal.
            except Exception as error:
                print(
                    f"\n[ SimJowBot ] ERROR: Retweet not successful. Reason:\n{error}"
                )
            else:
                print(f"\n[ SimJowBot ] Retweet published successfully.")


if __name__ == "__main__":

    hashtagsKeywordList = [
        "الکترونیک",
        "رباتیک",
        "آردوینو",
        "arduino",
        "rasperrypi",
        "vhdl",
        "verilog",
        "pcb",
        "fpga",
        "میکروکنترلر",
        "سیمجو",
        "سیم‌جو",
        "سیم_جو",
        "AppleEvent",
    ]

    hashtagsFinalList = []
    for i in range(len(hashtagsKeywordList)):
        tmpStr = "#" + hashtagsKeywordList.pop()
        hashtagsFinalList.append(tmpStr)

    # create a tweepy Stream object for real time filtering of latest posted tweets
    stream = SimJowStream(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
    stream.filter(track=hashtagsFinalList, languages=["fa"])
