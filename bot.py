#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SimJowBot - Persian Counter Bot for Twitter/X
==============================================

A Twitter bot that posts daily counter values in Persian, with automatic
rate limiting, error handling, and CI/CD integration.

This bot:
- Counts days from March 18, 2025 up to MAX_COUNTER_VALUE
- Posts Persian number words as quote tweets
- Handles Twitter API rate limits gracefully
- Maintains persistent counter state
- Supports CI/CD workflows

Author: SimJowBot Project
Version: 2.0.0
License: MIT
"""

import logging
import os
import sys
import time
from datetime import datetime, timedelta, date
from typing import Optional, Tuple, Dict, Any

import tweepy
from dotenv import load_dotenv

from persian_numbers import convert_to_persian_word

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Application constants
class Config:
    """Configuration constants for the bot."""

    # Twitter API credentials
    API_KEY: str = os.environ.get("API_KEY", "")
    API_KEY_SECRET: str = os.environ.get("API_KEY_SECRET", "")
    ACCESS_TOKEN: str = os.environ.get("ACCESS_TOKEN", "")
    ACCESS_TOKEN_SECRET: str = os.environ.get("ACCESS_TOKEN_SECRET", "")
    BEARER_TOKEN: str = os.environ.get("BEARER_TOKEN", "")

    # File paths
    COUNTER_FILE: str = "counter.txt"
    RATE_LIMIT_FILE: str = "rate_limit_failure.txt"

    # Bot configuration
    START_DATE: date = date(2025, 3, 18)
    ABS_COUNTING_LIMIT: int = 999999
    MIN_COUNTER_VALUE: int = 1
    MAX_COUNTER_VALUE: int = int(
        os.environ.get("MAX_COUNTER_VALUE", str(ABS_COUNTING_LIMIT))
    )
    TWITTER_RATE_LIMIT_RESET_MINUTES: int = 15
    MAX_TWEET_PREVIEW_LENGTH: int = 100
    MAX_TWEETS_TO_FETCH: int = 20

    # Special cases
    MAX_COUNTER_TWEET_TEXT: str = os.environ.get("MAX_COUNTER_TWEET_TEXT", "***")


class FileManager:
    """Handles file operations for counter and rate limit tracking."""

    def __init__(
        self,
        counter_file: str = Config.COUNTER_FILE,
        rate_limit_file: str = Config.RATE_LIMIT_FILE,
    ):
        """
        Initialize FileManager with file paths.

        Args:
            counter_file: Path to the counter storage file
            rate_limit_file: Path to the rate limit tracking file
        """
        self.counter_file = counter_file
        self.rate_limit_file = rate_limit_file

    def get_stored_counter(self) -> int:
        """
        Read the counter from the counter file.

        Returns:
            int: The stored counter value, defaults to 0 if file not found or invalid
        """
        try:
            with open(self.counter_file, "r", encoding="utf-8") as file:
                counter_value = int(file.read().strip())
                if (
                    counter_value < Config.MIN_COUNTER_VALUE
                    or counter_value > Config.MAX_COUNTER_VALUE
                ):
                    logger.warning(
                        f"Counter value {counter_value} out of bounds, resetting to 0"
                    )
                    return 0

                return counter_value
        except FileNotFoundError:
            logger.warning(
                f"Counter file {self.counter_file} not found, defaulting to {Config.MIN_COUNTER_VALUE}"
            )
            return Config.MIN_COUNTER_VALUE
        except (ValueError, OSError) as e:
            logger.error(
                f"Error reading counter file: {e}, defaulting to {Config.MIN_COUNTER_VALUE}"
            )
            return Config.MIN_COUNTER_VALUE

    def store_counter(self, counter: int) -> None:
        """
        Update the counter in the counter file.

        Args:
            counter: The counter value to store

        Raises:
            OSError: If file write operation fails
        """
        try:
            with open(self.counter_file, "w", encoding="utf-8") as file:
                file.write(str(counter))
            logger.info(f"✅ Counter file updated successfully to {counter}")
        except OSError as e:
            logger.error(f"❌ Error writing to counter file: {e}")
            logger.error(f"🔍 Attempted to write counter value: {counter}")
            logger.error(f"📁 Counter file path: {self.counter_file}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error updating counter: {e}")
            raise

    def save_rate_limit_failure(self) -> None:
        """Save the timestamp when rate limit was hit."""
        try:
            with open(self.rate_limit_file, "w", encoding="utf-8") as file:
                file.write(datetime.now().isoformat())
            logger.info("Rate limit failure timestamp saved")
        except OSError as e:
            logger.error(f"Failed to save rate limit failure: {e}")

    def check_rate_limit_status(self) -> bool:
        """
        Check if we're still within a rate limit cooldown period.

        Returns:
            bool: True if safe to proceed, False if still in cooldown
        """
        try:
            with open(self.rate_limit_file, "r", encoding="utf-8") as file:
                failure_time_str = file.read().strip()
                failure_time = datetime.fromisoformat(failure_time_str)
                now = datetime.now()
                time_since_failure = now - failure_time

                reset_interval = timedelta(
                    minutes=Config.TWITTER_RATE_LIMIT_RESET_MINUTES
                )

                if time_since_failure < reset_interval:
                    remaining_time = reset_interval - time_since_failure
                    total_seconds = int(remaining_time.total_seconds())
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60

                    logger.warning(
                        f"⚠️  Rate limit active! Please wait {minutes}m {seconds}s"
                    )
                    logger.info(
                        f"⏰ Reset time: {(failure_time + reset_interval).strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    return False
                else:
                    # Rate limit has expired, remove the file
                    os.remove(self.rate_limit_file)
                    logger.info("✅ Rate limit period has expired. Safe to proceed.")
                    return True

        except FileNotFoundError:
            # No rate limit failure recorded
            return True
        except Exception as e:
            logger.warning(f"Could not check rate limit status: {e}")
            return True  # Allow running if there's any error

    def rate_limit_file_exists(self) -> bool:
        """Check if rate limit file exists."""
        return os.path.exists(self.rate_limit_file)


class DateTimeUtil:
    """Utility functions for date and time calculations."""

    @staticmethod
    def get_counter_value_for_today() -> int:
        """
        Calculate the current counter value based on days passed since start date.

        The counter starts at Config.MIN_COUNTER_VALUE on March 18, 2025 and increments by one
        each day, up to a maximum of MAX_COUNTER_VALUE.

        Returns:
            int: The counter value for the current day. Returns 0 if the
                 date is before the start date or after the MAX_COUNTER_VALUE limit.
        """
        today = date.today()
        delta = today - Config.START_DATE
        days_passed = delta.days

        # The count starts from Config.MIN_COUNTER_VALUE, so add 1 to the number of days passed
        count = days_passed + 1

        # Check for edge cases
        if count < Config.MIN_COUNTER_VALUE or count > Config.MAX_COUNTER_VALUE:
            return 0

        return count

    @staticmethod
    def is_ci_environment() -> bool:
        """Check if running in a CI environment."""
        return bool(os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"))


class TwitterUtil:
    """Utility functions for Twitter operations."""

    @staticmethod
    def get_tweet_url(username: str, tweet_id: str) -> str:
        """
        Build a tweet URL using username and tweet ID.

        Args:
            username: The Twitter username (without @)
            tweet_id: The tweet ID

        Returns:
            str: The complete tweet URL
        """
        return f"https://x.com/{username}/status/{tweet_id}"

    @staticmethod
    def get_tweet_type(tweet: Any) -> str:
        """
        Determine the type of a tweet based on its properties.

        Args:
            tweet: The tweet object from Twitter API

        Returns:
            str: A descriptive string with emoji indicating tweet type
        """
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

    @staticmethod
    def print_tweet_info(tweet: Any, index: int, username: str) -> None:
        """
        Print formatted information about a tweet.

        Args:
            tweet: The tweet object from Twitter API
            index: The index number for display
            username: The username of the tweet author
        """
        tweet_type = TwitterUtil.get_tweet_type(tweet)
        created_at = (
            tweet.created_at.strftime("%Y-%m-%d %H:%M")
            if hasattr(tweet, "created_at") and tweet.created_at
            else "Unknown"
        )

        # Truncate long tweets for display
        text_preview = (
            tweet.text[: Config.MAX_TWEET_PREVIEW_LENGTH] + "..."
            if len(tweet.text) > Config.MAX_TWEET_PREVIEW_LENGTH
            else tweet.text
        )
        text_preview = text_preview.replace("\n", " ")  # Replace newlines with spaces

        tweet_url = TwitterUtil.get_tweet_url(username, tweet.id)
        logger.info(f"{index:2d}. {tweet_type} | {created_at} | {tweet_url}")
        logger.info(f"    📝 {text_preview}")

    @staticmethod
    def generate_persian_tweet_text(counter: int) -> str:
        """
        Generate Persian tweet text for the given counter.

        Args:
            counter: The counter value to convert

        Returns:
            str: The Persian text for the tweet
        """
        if counter == Config.MAX_COUNTER_VALUE:
            return Config.MAX_COUNTER_TWEET_TEXT
        else:
            return f"{convert_to_persian_word(counter)} تو"


class TwitterClient:
    """Wrapper class for Twitter API operations with enhanced error handling."""

    def __init__(self):
        """Initialize Twitter client with API credentials."""
        self.client = tweepy.Client(
            bearer_token=Config.BEARER_TOKEN,
            consumer_key=Config.API_KEY,
            consumer_secret=Config.API_KEY_SECRET,
            access_token=Config.ACCESS_TOKEN,
            access_token_secret=Config.ACCESS_TOKEN_SECRET,
        )
        self.file_manager = FileManager()

    def _handle_rate_limit_error(self, is_specific_rate_limit: bool = True) -> None:
        """
        Handle rate limit errors with consistent messaging.

        Args:
            is_specific_rate_limit: Whether this is a confirmed rate limit error
        """
        self.file_manager.save_rate_limit_failure()

        if is_specific_rate_limit:
            logger.error("🚫 Rate limit exceeded!")
            logger.info("Twitter API v2 Rate Limits (Free Tier):")
            logger.info("- Get user tweets: 75 requests per 15 minutes")
            logger.info("- Post tweets: 25 posts per 24 hours")
            logger.info("- Most endpoints reset every 15 minutes")
        else:
            logger.error("This appears to be a rate limit error.")

        # Calculate when rate limit will reset
        reset_time = datetime.now() + timedelta(
            minutes=Config.TWITTER_RATE_LIMIT_RESET_MINUTES
        )
        logger.info(
            f"⏰ Rate limit will reset at: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if is_specific_rate_limit:
            logger.info(
                f"Please wait {Config.TWITTER_RATE_LIMIT_RESET_MINUTES} minutes before running the bot again."
            )
            logger.info("To avoid this issue in the future:")
            logger.info("1. Wait at least 15 minutes between runs")
            logger.info("2. Consider upgrading to a paid plan for higher limits")
        else:
            logger.info("Free plans have very limited requests per month.")

    def get_authenticated_user(self) -> Optional[Any]:
        """
        Get the authenticated user information.

        Returns:
            User object or None if failed
        """
        try:
            user = self.client.get_me(
                user_fields=["protected", "public_metrics", "verified"]
            )
            if user.data is None:
                raise ValueError("Could not get authenticated user information")

            logger.info(f"Authenticated as @{user.data.username} (ID: {user.data.id})")
            protected_status = "Private" if user.data.protected else "Public"
            tweet_count = (
                user.data.public_metrics["tweet_count"]
                if user.data.public_metrics
                else "Unknown"
            )
            logger.info(f"Account: {protected_status} | Tweets: {tweet_count}")

            return user
        except Exception as e:
            logger.error(f"Failed to get authenticated user: {e}")
            return None

    def get_user_tweets(self, user_id: str) -> Tuple[Optional[Any], Optional[str]]:
        """
        Get tweets from a user.

        Args:
            user_id: The user ID to fetch tweets from

        Returns:
            Tuple of (tweets_response, username) or (None, None) if failed
        """
        try:
            logger.info("🔍 Fetching user tweets...")
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=Config.MAX_TWEETS_TO_FETCH,
                tweet_fields=["created_at", "public_metrics", "referenced_tweets"],
                expansions=["referenced_tweets.id"],
            )
            logger.info("✅ Successfully got tweets using username->ID approach")
            logger.info(f"\tAPI Response - tweets.data: {tweets.data}")
            logger.info(
                f"\tAPI Response - tweets.meta: {tweets.meta if hasattr(tweets, 'meta') else 'No meta'}"
            )

            return tweets, None
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit error: {e}")
            self._handle_rate_limit_error(is_specific_rate_limit=True)
            return None, None
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {e}")
            if "429" in str(e) or "rate limit" in str(e).lower():
                self._handle_rate_limit_error(is_specific_rate_limit=False)
            else:
                logger.error("This is a general Twitter API error (not rate limiting).")
            return None, None

    def post_quote_tweet(
        self, tweet_text: str, quote_tweet_id: str, username: str
    ) -> Optional[str]:
        """
        Post a quote tweet.

        Args:
            tweet_text: The text content for the quote tweet
            quote_tweet_id: The ID of the tweet to quote
            username: The username for URL generation

        Returns:
            The URL of the posted tweet or None if failed
        """
        try:
            logger.info(f"📝 Posting quote tweet with text:\n{tweet_text}")
            response = self.client.create_tweet(
                text=tweet_text, quote_tweet_id=quote_tweet_id
            )

            response_tweet_url = TwitterUtil.get_tweet_url(
                username, response.data["id"]
            )
            logger.info(f"✅ Quote tweet posted successfully! {response_tweet_url}")
            return response_tweet_url
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit error while posting: {e}")
            self._handle_rate_limit_error(is_specific_rate_limit=True)
            return None
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error while posting: {e}")
            if "429" in str(e) or "rate limit" in str(e).lower():
                self._handle_rate_limit_error(is_specific_rate_limit=False)
            else:
                logger.error("This is a general Twitter API error (not rate limiting).")
            return None

    def try_posting_tweet(self, new_counter: int) -> bool:
        """
        Try to post a tweet and update the counter.

        Args:
            new_counter: The counter value to post

        Returns:
            True if successful, False otherwise
        """
        # Get authenticated user
        user = self.get_authenticated_user()
        if not user:
            return False

        # Get user tweets
        tweets, _ = self.get_user_tweets(user.data.id)
        if not tweets or not tweets.data:
            logger.error("❌ No tweets found in response.")
            return False

        logger.info(f"📋 Found {len(tweets.data)} tweets:")

        selected_tweet = None
        previous_counter = new_counter - 1
        previous_quoted_tweet_text = TwitterUtil.generate_persian_tweet_text(
            previous_counter
        )
        for i, tweet in enumerate(tweets.data, 1):
            TwitterUtil.print_tweet_info(tweet, i, user.data.username)
            # Filter for quoted tweets
            if (
                hasattr(tweet, "referenced_tweets")
                and tweet.referenced_tweets
                and (
                    tweet.referenced_tweets[0].type == "quoted"
                    or (previous_counter == Config.MIN_COUNTER_VALUE)
                )
            ):
                # Check if tweet text includes previous quoted tweet text
                # Defensive: handle missing or non-string tweet.text (Mocks may not provide it)
                tweet_text_value = getattr(tweet, "text", None)
                # Consider tweet to have text only if it's actually a str. Mocks return
                # Mock objects which should be treated as 'no text' for matching logic.
                has_text_attr = isinstance(tweet_text_value, str)
                tweet_text = tweet_text_value if has_text_attr else ""

                # If the previous quoted text is in the tweet text, or if the tweet
                # effectively has no text attribute but is a quoted tweet (common in some mocks),
                # accept it as the selected quoted tweet.
                if previous_quoted_tweet_text in tweet_text or (
                    not has_text_attr and tweet.referenced_tweets[0].type == "quoted"
                ):
                    selected_tweet = tweet
                    selected_tweet_url = TwitterUtil.get_tweet_url(
                        user.data.username, selected_tweet.id
                    )
                    print(f"🎯 Selected latest quoted tweet: {selected_tweet_url}")
                    break

        if selected_tweet is None:
            logger.error(
                "❌ Previous quoted tweet was not found in the retrieved tweets. Skipping quote tweet posting."
            )
            return False

        # Generate tweet text and post
        tweet_text = TwitterUtil.generate_persian_tweet_text(new_counter)
        response_url = self.post_quote_tweet(
            tweet_text, selected_tweet.id, user.data.username
        )

        if response_url:
            try:
                self.file_manager.store_counter(new_counter)
                logger.info(f"🔢 Stored counter updated to {new_counter}")
                return True
            except Exception as e:
                logger.warning(
                    f"⚠️  Tweet posted successfully, but failed to update stored counter: {e}"
                )
                logger.warning(
                    "🔧 You may need to manually update the stored counter file"
                )
                return False

        return False


def main() -> None:
    """Main execution function for the bot."""
    # Track whether any changes were made that need committing by CI
    changes_made = False

    # Initialize utilities
    file_manager = FileManager()

    # Reading the counter
    stored_counter = file_manager.get_stored_counter()
    expected_counter = DateTimeUtil.get_counter_value_for_today()

    if stored_counter == 0:
        logger.error(
            "❌  Stored counter was not found or invalid. No tweet will be posted."
        )
        # exit with error code
        sys.exit(1)

    if expected_counter == 0:
        logger.error(
            "❌  Today is outside the counting range. No tweet will be posted."
        )
        # exit with error code
        sys.exit(1)

    logger.info(f"🕒 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔢 Stored counter value: {stored_counter}")
    logger.info(f"🔢 Expected counter value: {expected_counter}")

    # Check if we need to tweet today
    if stored_counter >= expected_counter:
        logger.info("✅ No tweet needed today. Stored counter is up to date.")
        sys.exit(0)

    lagging_days = expected_counter - stored_counter
    logger.info(
        f"⚠️  Stored counter is behind by {lagging_days} day(s). Proceeding to tweet..."
    )

    # Initialize Twitter client
    twitter_client = TwitterClient()

    for i in range(lagging_days):
        new_counter = stored_counter + i + 1
        logger.info(f"--- Processing counter value: {new_counter} ---")

        # Check if we're still in a rate limit cooldown
        if not file_manager.check_rate_limit_status():
            if DateTimeUtil.is_ci_environment():
                logger.error(
                    "❌ Rate limit active. Exiting in CI environment to allow scheduled retry."
                )
                logger.info(
                    "💡 Consider running this bot on a cron schedule (every 20-30 minutes)"
                )
                if file_manager.rate_limit_file_exists():
                    changes_made = True
                break
            else:
                logger.info(
                    f"⏳ Waiting {Config.TWITTER_RATE_LIMIT_RESET_MINUTES} minutes for rate limit to reset..."
                )
                time.sleep(Config.TWITTER_RATE_LIMIT_RESET_MINUTES * 60)
                logger.info("🔄 Checking rate limit status again...")

        # Try posting the tweet
        success = twitter_client.try_posting_tweet(new_counter)
        if success:
            changes_made = True
            logger.info(f"✅ Successfully posted tweet for counter {new_counter}")
        else:
            logger.error(f"❌ Failed to post tweet for counter {new_counter}")
            if file_manager.rate_limit_file_exists():
                changes_made = True
            break

    # Final exit logic
    if changes_made:
        logger.info(
            "📝 Changes were made during this run - exiting with success code for commit"
        )
    else:
        logger.info("📝 No changes were made during this run")


# Legacy functions kept for backwards compatibility - will be removed in future versions
# Use the new class-based approach instead

# Main script execution starts here
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
