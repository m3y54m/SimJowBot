import tweepy
import os
import time
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from persian_numbers import convert_to_persian_word

# Load environment variables from .env file
load_dotenv()

# Your Twitter API credentials
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

# File to store the counter
COUNTER_FILE = "counter.txt"
RATE_LIMIT_FILE = "rate_limit_failure.txt"

# Rate limit constants
TWITTER_RATE_LIMIT_RESET_MINUTES = 16


def read_counter():
    """Read the counter from the counter file"""
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 1
    except ValueError:
        return 1


def store_counter(counter):
    """Update the counter in the counter file"""
    try:
        with open(COUNTER_FILE, "w") as f:
            f.write(str(counter))
        print(f"✅ Counter file updated successfully to {counter}")
    except OSError as e:
        print(f"❌ Error writing to counter file: {e}")
        print(f"🔍 Attempted to write counter value: {counter}")
        print(f"📁 Counter file path: {COUNTER_FILE}")
        # Don't exit here - let the calling code decide how to handle this
        raise
    except Exception as e:
        print(f"❌ Unexpected error updating counter: {e}")
        raise


def get_tweet_url(username, tweet_id):
    """
    Build a tweet URL using username and tweet ID.

    Args:
        username (str): The Twitter username (without @)
        tweet_id (str or int): The tweet ID

    Returns:
        str: The complete tweet URL
    """
    return f"https://x.com/{username}/status/{tweet_id}"


def get_counter_value_for_today():
    """
    Calculates the current counter value based on the number of days
    passed since March 18, 2025.

    The counter starts at 1 on March 18, 2025 and increments by one
    each day, up to a maximum of 1000.

    Returns:
        int: The counter value for the current day. Returns 0 if the
             date is before the start date or after the 1000th day.
    """
    start_date = date(2025, 3, 18)
    today = date.today()

    # Calculate the difference in days
    delta = today - start_date
    days_passed = delta.days

    # The count starts from 1, so add 1 to the number of days passed.
    # The maximum count is 1000.
    count = days_passed + 1

    # Check for the edge cases
    if count < 1 or count > 1000:
        return 0
    else:
        return count


def save_rate_limit_failure():
    """Save the timestamp when rate limit was hit"""
    with open(RATE_LIMIT_FILE, "w") as f:
        f.write(datetime.now().isoformat())


def handle_rate_limit_error(is_specific_rate_limit=True):
    """Handle rate limit errors with consistent messaging"""
    save_rate_limit_failure()

    if is_specific_rate_limit:
        print("🚫 Rate limit exceeded!")
        print("\nTwitter API v2 Rate Limits (Free Tier):")
        print("- Get user tweets: 75 requests per 15 minutes")
        print("- Post tweets: 25 posts per 24 hours")
        print("- Most endpoints reset every 15 minutes")
    else:
        print("This appears to be a rate limit error.")

    # Calculate when rate limit will reset
    reset_time = datetime.now() + timedelta(minutes=TWITTER_RATE_LIMIT_RESET_MINUTES)
    print(f"\n⏰ Rate limit will reset at: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if is_specific_rate_limit:
        print(
            f"Please wait {TWITTER_RATE_LIMIT_RESET_MINUTES} minutes before running the bot again."
        )
        print(f"\nTo avoid this issue in the future:")
        print("1. Wait at least 15 minutes between runs")
        print("2. Consider upgrading to a paid plan for higher limits")
    else:
        print("Free plans have very limited requests per month.")


def get_tweet_type(tweet):
    """Determine the type of a tweet based on its properties"""
    if hasattr(tweet, "referenced_tweets") and tweet.referenced_tweets:
        ref_type = tweet.referenced_tweets[0].type
        if ref_type == "retweeted":
            return "🔄 Retweet"
        elif ref_type == "replied_to":
            return "💬 Reply"
        elif ref_type == "quoted":
            return "📝 Quote Tweet"

    # Check if it's a reply by looking at the text (starts with @username)
    if hasattr(tweet, "text") and tweet.text.startswith("@"):
        return "💬 Reply"

    return "📄 Original Tweet"


def print_tweet_info(tweet, index, username):
    """Print formatted information about a tweet"""
    tweet_type = get_tweet_type(tweet)
    created_at = (
        tweet.created_at.strftime("%Y-%m-%d %H:%M")
        if hasattr(tweet, "created_at") and tweet.created_at
        else "Unknown"
    )

    # Truncate long tweets for display
    text_preview = tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text
    text_preview = text_preview.replace("\n", " ")  # Replace newlines with spaces

    tweet_url = get_tweet_url(username, tweet.id)
    print(f"{index:2d}. {tweet_type} | {created_at} | {tweet_url}")
    print(f"    📝 {text_preview}")
    print()


def check_rate_limit_status():
    """Check if we're still within a rate limit cooldown period"""
    try:
        with open(RATE_LIMIT_FILE, "r") as f:
            failure_time_str = f.read().strip()
            failure_time = datetime.fromisoformat(failure_time_str)
            now = datetime.now()
            time_since_failure = now - failure_time

            # Twitter API rate limits reset every 15 minutes
            reset_interval = timedelta(minutes=TWITTER_RATE_LIMIT_RESET_MINUTES)

            if time_since_failure < reset_interval:
                remaining_time = reset_interval - time_since_failure
                total_seconds = int(remaining_time.total_seconds())
                minutes = total_seconds // 60
                seconds = total_seconds % 60

                print(f"⚠️  Rate limit active! Please wait {minutes}m {seconds}s")
                print(
                    f"⏰ Reset time: {(failure_time + reset_interval).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return False
            else:
                # Rate limit has expired, remove the file
                os.remove(RATE_LIMIT_FILE)
                print("✅ Rate limit period has expired. Safe to proceed.")
                return True

    except FileNotFoundError:
        # No rate limit failure recorded
        return True
    except Exception as e:
        print(f"Warning: Could not check rate limit status: {e}")
        return True  # Allow running if there's any error


def try_posting_tweet(client, new_counter):
    """
    Try to post a tweet and update the counter.
    Returns True if successful, False otherwise.
    """
    try:
        # 1. Get the authenticated user (current user)
        user = client.get_me(user_fields=["protected", "public_metrics", "verified"])
        if user.data is None:
            raise ValueError("Could not get authenticated user information")

        print(f"Authenticated as @{user.data.username} (ID: {user.data.id})")
        print(
            f"Account: {'Private' if user.data.protected else 'Public'} | Tweets: {user.data.public_metrics['tweet_count'] if user.data.public_metrics else 'Unknown'}"
        )

        print("\n🔍 Fetching user tweets...")

        # 2. Get tweets using user ID
        tweets = client.get_users_tweets(
            user.data.id,
            max_results=50,  # 5-100 is the allowed range
            tweet_fields=["created_at", "public_metrics", "referenced_tweets"],
            expansions=["referenced_tweets.id"],
        )
        print("✅ Successfully got tweets using username->ID approach")
        print(f"\tAPI Response - tweets.data: {tweets.data}")
        print(
            f"\tAPI Response - tweets.meta: {tweets.meta if hasattr(tweets, 'meta') else 'No meta'}"
        )

        if tweets.data:
            print(f"\n📋 Found {len(tweets.data)} tweets:")
            for i, tweet in enumerate(tweets.data, 1):
                print_tweet_info(tweet, i, user.data.username)

            # 3. Filter for quoted tweets first
            quoted_tweets = [
                tweet
                for tweet in tweets.data
                if hasattr(tweet, "referenced_tweets")
                and tweet.referenced_tweets
                and tweet.referenced_tweets[0].type == "quoted"
            ]

            if quoted_tweets:
                # Select the latest quoted tweet (first in the filtered list)
                selected_tweet = quoted_tweets[0]
                selected_tweet_url = get_tweet_url(
                    user.data.username, selected_tweet.id
                )
                print(f"🎯 Selected latest quoted tweet: {selected_tweet_url}")
              
                # 4. Post a quote tweet with the new_counter in Persian words

                if new_counter == 1000:
                    tweet_text = "هزارتو"
                else:
                    tweet_text = f"{convert_to_persian_word(new_counter)} تو"

                print(f"📝 Posting quote tweet with text:\n{tweet_text}")

                response = client.create_tweet(
                    text=tweet_text, quote_tweet_id=selected_tweet.id
                )

                response_tweet_url = get_tweet_url(
                    user.data.username, response.data["id"]
                )
                print(f"✅ Quote tweet posted successfully! {response_tweet_url}")

                try:
                    store_counter(new_counter)
                    print(f"🔢 Stored counter updated to {new_counter}")
                    return True  # Successfully posted and updated counter
                except Exception as e:
                    print(
                        f"⚠️  Tweet posted successfully, but failed to update stored counter: {e}"
                    )
                    print("🔧 You may need to manually update the stored counter file")
                    return False  # Tweet posted but counter update failed
            else:
                print(
                    f"❌ No quoted tweets found in the retrieved tweets. Skipping quote tweet posting."
                )
                return False  # No quoted tweets found
        else:
            print("❌ No tweets found in response.")
            return False  # No tweets to quote

    except tweepy.TooManyRequests as e:
        print(f"Rate limit error: {e}")
        handle_rate_limit_error(is_specific_rate_limit=True)
        return False  # Rate limited
    except tweepy.TweepyException as e:
        print(f"An error occurred: {e}")
        # Check if it's a rate limit error that wasn't caught by TooManyRequests
        if "429" in str(e) or "rate limit" in str(e).lower():
            handle_rate_limit_error(is_specific_rate_limit=False)
        else:
            print("This is a general Twitter API error (not rate limiting).")
        return False  # Other Twitter API error


# Main script execution starts here

# Track whether any changes were made that need committing by CI
changes_made = False

# --- Reading the counter ---
stored_counter = read_counter()
expected_counter = get_counter_value_for_today()

print(f"🕒 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔢 Stored counter value: {stored_counter}")
print(f"🔢 Expected counter value: {expected_counter}\n")

# --- Check if we need to tweet today ---
if stored_counter >= expected_counter:
    print("✅ No tweet needed today. Stored counter is up to date.")
    exit(0)
else:
    lagging_days = expected_counter - stored_counter
    print(
        f"⚠️  Stored counter is behind by {lagging_days} day(s). Proceeding to tweet..."
    )

    # --- Authenticate with the Twitter API ---
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    for i in range(lagging_days):
        new_counter = stored_counter + i + 1
        print(f"\n--- Processing counter value: {new_counter} ---")

        # --- Check if we're still in a rate limit cooldown ---
        # In CI environments (like GitHub Actions), fail fast instead of waiting
        is_ci_environment = os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")

        if not check_rate_limit_status():
            if is_ci_environment:
                print(
                    "❌ Rate limit active. Exiting in CI environment to allow scheduled retry."
                )
                print(
                    "💡 Consider running this bot on a cron schedule (every 20-30 minutes)"
                )
                # If rate limit file exists, it means we need to commit it
                if os.path.exists(RATE_LIMIT_FILE):
                    changes_made = True
                break  # Exit the loop instead of exit(1)
            else:
                print(
                    f"⏳ Waiting {TWITTER_RATE_LIMIT_RESET_MINUTES} minutes for rate limit to reset..."
                )
                time.sleep(
                    TWITTER_RATE_LIMIT_RESET_MINUTES * 60
                )  # Convert minutes to seconds
                print("🔄 Checking rate limit status again...")

        # --- Try posting the tweet ---
        success = try_posting_tweet(client, new_counter)
        if success:
            changes_made = True
            print(f"✅ Successfully posted tweet for counter {new_counter}")
        else:
            print(f"❌ Failed to post tweet for counter {new_counter}")
            # If we hit rate limits or other errors, save the rate limit file
            # and exit so the workflow can commit any successful changes
            if os.path.exists(RATE_LIMIT_FILE):
                changes_made = True
            break  # Exit the loop on any failure

# --- Final exit logic ---
if changes_made:
    print("📝 Changes were made during this run - exiting with success code for commit")
    exit(0)
else:
    print("📝 No changes were made during this run")
    exit(0)
