#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for bot.py
===================================

This module contains unit tests for all components of the SimJowBot Twitter bot,
including mocked Twitter API interactions, file operations, and utility functions.

Tests follow TDD principles with comprehensive mocking to avoid external dependencies.

Author: SimJowBot Project
Version: 2.0.0
"""

import unittest
import tempfile
import shutil
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, date, timedelta
from typing import Any

# Add parent directory to path to import bot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bot
from bot import Config, FileManager, TwitterClient, DateTimeUtil, TwitterUtil, main
import tweepy


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def setUp(self):
        """Set up test environment."""
        # Save original environment variables
        self.original_env = {}
        for key in [
            "API_KEY",
            "API_KEY_SECRET",
            "ACCESS_TOKEN",
            "ACCESS_TOKEN_SECRET",
            "BEARER_TOKEN",
        ]:
            self.original_env[key] = os.environ.get(key)

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

    def test_config_default_values(self):
        """Test Config class default values."""
        self.assertEqual(Config.COUNTER_FILE, "counter.txt")
        self.assertEqual(Config.RATE_LIMIT_FILE, "rate_limit_failure.txt")
        self.assertEqual(Config.START_DATE, date(2025, 3, 18))
        self.assertEqual(Config.MAX_COUNTER, 1000)
        self.assertEqual(Config.TWITTER_RATE_LIMIT_RESET_MINUTES, 16)
        self.assertEqual(Config.MAX_TWEET_PREVIEW_LENGTH, 100)
        self.assertEqual(Config.MAX_TWEETS_TO_FETCH, 50)
        self.assertEqual(Config.HEZARTOO_TEXT, "هزارتو")

    def test_config_environment_variables(self):
        """Test Config reads environment variables correctly."""
        # Set test environment variables
        test_env = {
            "API_KEY": "test_api_key",
            "API_KEY_SECRET": "test_api_secret",
            "ACCESS_TOKEN": "test_access_token",
            "ACCESS_TOKEN_SECRET": "test_access_secret",
            "BEARER_TOKEN": "test_bearer_token",
        }

        for key, value in test_env.items():
            os.environ[key] = value

        # Reload the Config class to pick up new environment variables
        import importlib

        importlib.reload(bot)

        # Test that Config picks up the environment variables
        self.assertEqual(bot.Config.API_KEY, "test_api_key")
        self.assertEqual(bot.Config.API_KEY_SECRET, "test_api_secret")
        self.assertEqual(bot.Config.ACCESS_TOKEN, "test_access_token")
        self.assertEqual(bot.Config.ACCESS_TOKEN_SECRET, "test_access_secret")
        self.assertEqual(bot.Config.BEARER_TOKEN, "test_bearer_token")


class TestDateTimeUtil(unittest.TestCase):
    """Test cases for the DateTimeUtil class."""

    def test_get_counter_value_for_today_start_date(self):
        """Test counter value on the start date."""
        with patch("bot.date") as mock_date:
            mock_date.today.return_value = date(2025, 3, 18)  # Start date
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            result = DateTimeUtil.get_counter_value_for_today()
            self.assertEqual(result, 1)

    def test_get_counter_value_for_today_second_day(self):
        """Test counter value on the second day."""
        with patch("bot.date") as mock_date:
            mock_date.today.return_value = date(2025, 3, 19)  # Second day
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            result = DateTimeUtil.get_counter_value_for_today()
            self.assertEqual(result, 2)

    def test_get_counter_value_for_today_max_day(self):
        """Test counter value on the 1000th day."""
        with patch("bot.date") as mock_date:
            # 1000 days after start date (March 18, 2025 + 999 days)
            # March 18, 2025 + 999 days = December 12, 2027
            mock_date.today.return_value = date(2027, 12, 12)
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            result = DateTimeUtil.get_counter_value_for_today()
            self.assertEqual(result, 1000)

    def test_get_counter_value_for_today_before_start(self):
        """Test counter value before start date."""
        with patch("bot.date") as mock_date:
            mock_date.today.return_value = date(2025, 3, 17)  # Before start
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            result = DateTimeUtil.get_counter_value_for_today()
            self.assertEqual(result, 0)

    def test_get_counter_value_for_today_after_max(self):
        """Test counter value after 1000 days."""
        with patch("bot.date") as mock_date:
            mock_date.today.return_value = date(2027, 12, 14)  # Day 1001
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

            result = DateTimeUtil.get_counter_value_for_today()
            self.assertEqual(result, 0)

    def test_is_ci_environment_github_actions(self):
        """Test CI environment detection with GITHUB_ACTIONS."""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            self.assertTrue(DateTimeUtil.is_ci_environment())

    def test_is_ci_environment_ci_var(self):
        """Test CI environment detection with CI variable."""
        with patch.dict(os.environ, {"CI": "true"}):
            self.assertTrue(DateTimeUtil.is_ci_environment())

    def test_is_ci_environment_false(self):
        """Test CI environment detection returns False when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(DateTimeUtil.is_ci_environment())


class TestTwitterUtil(unittest.TestCase):
    """Test cases for the TwitterUtil class."""

    def test_get_tweet_url(self):
        """Test tweet URL generation."""
        username = "testuser"
        tweet_id = "1234567890"
        expected = "https://x.com/testuser/status/1234567890"

        result = TwitterUtil.get_tweet_url(username, tweet_id)
        self.assertEqual(result, expected)

    def test_get_tweet_type_quote_tweet(self):
        """Test tweet type detection for quote tweets."""
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = [Mock(type="quoted")]

        result = TwitterUtil.get_tweet_type(mock_tweet)
        self.assertEqual(result, "📝 Quote Tweet")

    def test_get_tweet_type_retweet(self):
        """Test tweet type detection for retweets."""
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = [Mock(type="retweeted")]

        result = TwitterUtil.get_tweet_type(mock_tweet)
        self.assertEqual(result, "🔄 Retweet")

    def test_get_tweet_type_reply(self):
        """Test tweet type detection for replies."""
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = [Mock(type="replied_to")]

        result = TwitterUtil.get_tweet_type(mock_tweet)
        self.assertEqual(result, "💬 Reply")

    def test_get_tweet_type_reply_by_text(self):
        """Test tweet type detection for replies by text content."""
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = None
        mock_tweet.text = "@someone This is a reply"

        result = TwitterUtil.get_tweet_type(mock_tweet)
        self.assertEqual(result, "💬 Reply")

    def test_get_tweet_type_original(self):
        """Test tweet type detection for original tweets."""
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = None
        mock_tweet.text = "This is an original tweet"

        result = TwitterUtil.get_tweet_type(mock_tweet)
        self.assertEqual(result, "📄 Original Tweet")

    @patch("bot.logger")
    def test_print_tweet_info(self, mock_logger):
        """Test tweet information printing."""
        mock_tweet = Mock()
        mock_tweet.id = "1234567890"
        mock_tweet.text = "Test tweet content"
        mock_tweet.created_at = datetime(2025, 9, 12, 15, 30)
        mock_tweet.referenced_tweets = None

        TwitterUtil.print_tweet_info(mock_tweet, 1, "testuser")

        # Verify logger was called
        self.assertTrue(mock_logger.info.called)

        # Check that the log messages contain expected content
        call_args = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertTrue(any("📄 Original Tweet" in arg for arg in call_args))
        self.assertTrue(any("Test tweet content" in arg for arg in call_args))

    def test_generate_persian_tweet_text_regular(self):
        """Test Persian tweet text generation for regular numbers."""
        with patch("bot.convert_to_persian_word", return_value="بیست و سه"):
            result = TwitterUtil.generate_persian_tweet_text(23)
            self.assertEqual(result, "بیست و سه تو")

    def test_generate_persian_tweet_text_thousand(self):
        """Test Persian tweet text generation for 1000."""
        result = TwitterUtil.generate_persian_tweet_text(1000)
        self.assertEqual(result, "هزارتو")


class TestFileManager(unittest.TestCase):
    """Test cases for the FileManager class."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.counter_file = os.path.join(self.test_dir, "test_counter.txt")
        self.rate_limit_file = os.path.join(self.test_dir, "test_rate_limit.txt")
        self.file_manager = FileManager(self.counter_file, self.rate_limit_file)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_read_counter_file_exists(self):
        """Test reading counter when file exists."""
        with open(self.counter_file, "w") as f:
            f.write("42")

        result = self.file_manager.get_stored_counter()
        self.assertEqual(result, 42)

    def test_read_counter_file_not_exists(self):
        """Test reading counter when file doesn't exist."""
        result = self.file_manager.get_stored_counter()
        self.assertEqual(result, 1)

    def test_read_counter_invalid_content(self):
        """Test reading counter with invalid content."""
        with open(self.counter_file, "w") as f:
            f.write("invalid")

        result = self.file_manager.get_stored_counter()
        self.assertEqual(result, 1)

    def test_store_counter_success(self):
        """Test storing counter successfully."""
        self.file_manager.store_counter(123)

        with open(self.counter_file, "r") as f:
            content = f.read()

        self.assertEqual(content, "123")

    def test_store_counter_permission_error(self):
        """Test storing counter with permission error."""
        # Mock open to raise PermissionError
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(PermissionError):
                self.file_manager.store_counter(123)

    def test_save_rate_limit_failure(self):
        """Test saving rate limit failure timestamp."""
        with patch("bot.datetime") as mock_datetime:
            mock_now = datetime(2025, 9, 12, 15, 30, 45)
            mock_datetime.now.return_value = mock_now

            self.file_manager.save_rate_limit_failure()

            with open(self.rate_limit_file, "r") as f:
                content = f.read()

            self.assertEqual(content, mock_now.isoformat())

    def test_check_rate_limit_status_no_file(self):
        """Test rate limit status when no file exists."""
        result = self.file_manager.check_rate_limit_status()
        self.assertTrue(result)

    def test_check_rate_limit_status_expired(self):
        """Test rate limit status when limit has expired."""
        # Create a rate limit file with old timestamp
        old_time = datetime.now() - timedelta(minutes=20)
        with open(self.rate_limit_file, "w") as f:
            f.write(old_time.isoformat())

        # Mock os.remove to avoid Windows file locking issues
        with patch("bot.os.remove") as mock_remove:
            result = self.file_manager.check_rate_limit_status()
            self.assertTrue(result)

            # Verify remove was called
            mock_remove.assert_called_once_with(self.rate_limit_file)

    def test_check_rate_limit_status_active(self):
        """Test rate limit status when limit is still active."""
        # Create a rate limit file with recent timestamp
        recent_time = datetime.now() - timedelta(minutes=5)
        with open(self.rate_limit_file, "w") as f:
            f.write(recent_time.isoformat())

        result = self.file_manager.check_rate_limit_status()
        self.assertFalse(result)

    def test_rate_limit_file_exists_true(self):
        """Test rate limit file existence check when file exists."""
        with open(self.rate_limit_file, "w") as f:
            f.write("test")

        result = self.file_manager.rate_limit_file_exists()
        self.assertTrue(result)

    def test_rate_limit_file_exists_false(self):
        """Test rate limit file existence check when file doesn't exist."""
        result = self.file_manager.rate_limit_file_exists()
        self.assertFalse(result)


class TestTwitterClient(unittest.TestCase):
    """Test cases for the TwitterClient class."""

    def setUp(self):
        """Set up test environment."""
        # Mock the FileManager to avoid file operations
        with patch("bot.FileManager"):
            self.twitter_client = TwitterClient()

        # Mock the tweepy client
        self.mock_client = Mock()
        self.twitter_client.client = self.mock_client
        self.twitter_client.file_manager = Mock()

    def test_init_creates_client(self):
        """Test TwitterClient initialization."""
        with patch("bot.tweepy.Client") as mock_tweepy_client:
            with patch("bot.FileManager"):
                # Don't check exact credentials as they come from environment
                client = TwitterClient()

            # Just verify that tweepy.Client was called
            mock_tweepy_client.assert_called_once()

    @patch("bot.logger")
    def test_handle_rate_limit_error_specific(self, mock_logger):
        """Test rate limit error handling for specific errors."""
        self.twitter_client._handle_rate_limit_error(is_specific_rate_limit=True)

        # Verify file manager was called to save failure
        self.twitter_client.file_manager.save_rate_limit_failure.assert_called_once()

        # Verify appropriate log messages
        self.assertTrue(mock_logger.error.called)
        self.assertTrue(mock_logger.info.called)

    @patch("bot.logger")
    def test_handle_rate_limit_error_general(self, mock_logger):
        """Test rate limit error handling for general errors."""
        self.twitter_client._handle_rate_limit_error(is_specific_rate_limit=False)

        # Verify file manager was called to save failure
        self.twitter_client.file_manager.save_rate_limit_failure.assert_called_once()

        # Verify appropriate log messages
        self.assertTrue(mock_logger.error.called)
        self.assertTrue(mock_logger.info.called)

    @patch("bot.logger")
    def test_get_authenticated_user_success(self, mock_logger):
        """Test successful user authentication."""
        # Mock successful response
        mock_user_data = Mock()
        mock_user_data.username = "testuser"
        mock_user_data.id = "123456789"
        mock_user_data.protected = False
        mock_user_data.public_metrics = {"tweet_count": 100}

        mock_response = Mock()
        mock_response.data = mock_user_data

        self.mock_client.get_me.return_value = mock_response

        result = self.twitter_client.get_authenticated_user()

        self.assertEqual(result, mock_response)
        self.mock_client.get_me.assert_called_once_with(
            user_fields=["protected", "public_metrics", "verified"]
        )
        self.assertTrue(mock_logger.info.called)

    @patch("bot.logger")
    def test_get_authenticated_user_no_data(self, mock_logger):
        """Test user authentication when no data returned."""
        mock_response = Mock()
        mock_response.data = None

        self.mock_client.get_me.return_value = mock_response

        result = self.twitter_client.get_authenticated_user()

        self.assertIsNone(result)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.logger")
    def test_get_authenticated_user_exception(self, mock_logger):
        """Test user authentication with exception."""
        self.mock_client.get_me.side_effect = Exception("API Error")

        result = self.twitter_client.get_authenticated_user()

        self.assertIsNone(result)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.logger")
    def test_get_user_tweets_success(self, mock_logger):
        """Test successful tweet retrieval."""
        mock_tweets = Mock()
        mock_tweets.data = [Mock(), Mock()]
        mock_tweets.meta = {"result_count": 2}

        self.mock_client.get_users_tweets.return_value = mock_tweets

        tweets, username = self.twitter_client.get_user_tweets("123456789")

        self.assertEqual(tweets, mock_tweets)
        self.assertIsNone(username)
        self.mock_client.get_users_tweets.assert_called_once()
        self.assertTrue(mock_logger.info.called)

    @patch("bot.logger")
    def test_get_user_tweets_rate_limit(self, mock_logger):
        """Test tweet retrieval with rate limit error."""
        # Create a mock response for TooManyRequests
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.json.return_value = {
            "errors": [{"message": "Rate limit exceeded"}]
        }

        self.mock_client.get_users_tweets.side_effect = tweepy.TooManyRequests(
            mock_response
        )

        tweets, username = self.twitter_client.get_user_tweets("123456789")

        self.assertIsNone(tweets)
        self.assertIsNone(username)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.logger")
    def test_get_user_tweets_api_error(self, mock_logger):
        """Test tweet retrieval with general API error."""
        self.mock_client.get_users_tweets.side_effect = tweepy.TweepyException(
            "API Error"
        )

        tweets, username = self.twitter_client.get_user_tweets("123456789")

        self.assertIsNone(tweets)
        self.assertIsNone(username)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.logger")
    @patch("bot.TwitterUtil.get_tweet_url")
    def test_post_quote_tweet_success(self, mock_get_url, mock_logger):
        """Test successful quote tweet posting."""
        mock_response = Mock()
        mock_response.data = {"id": "987654321"}

        self.mock_client.create_tweet.return_value = mock_response
        mock_get_url.return_value = "https://x.com/testuser/status/987654321"

        result = self.twitter_client.post_quote_tweet(
            "Test text", "123456789", "testuser"
        )

        self.assertEqual(result, "https://x.com/testuser/status/987654321")
        self.mock_client.create_tweet.assert_called_once_with(
            text="Test text", quote_tweet_id="123456789"
        )
        self.assertTrue(mock_logger.info.called)

    @patch("bot.logger")
    def test_post_quote_tweet_rate_limit(self, mock_logger):
        """Test quote tweet posting with rate limit error."""
        # Create a mock response for TooManyRequests
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.json.return_value = {
            "errors": [{"message": "Rate limit exceeded"}]
        }

        self.mock_client.create_tweet.side_effect = tweepy.TooManyRequests(
            mock_response
        )

        result = self.twitter_client.post_quote_tweet(
            "Test text", "123456789", "testuser"
        )

        self.assertIsNone(result)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.logger")
    def test_post_quote_tweet_api_error(self, mock_logger):
        """Test quote tweet posting with general API error."""
        self.mock_client.create_tweet.side_effect = tweepy.TweepyException("API Error")

        result = self.twitter_client.post_quote_tweet(
            "Test text", "123456789", "testuser"
        )

        self.assertIsNone(result)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.TwitterUtil.print_tweet_info")
    @patch("bot.TwitterUtil.get_tweet_url")
    @patch("bot.TwitterUtil.generate_persian_tweet_text")
    @patch("bot.logger")
    def test_try_posting_tweet_success(
        self, mock_logger, mock_generate_text, mock_get_url, mock_print_info
    ):
        """Test successful complete tweet posting workflow."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.data.id = "123456789"
        mock_user.data.username = "testuser"

        # Mock tweets
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = [Mock(type="quoted")]
        mock_tweet.id = "tweet123"

        mock_tweets = Mock()
        mock_tweets.data = [mock_tweet]

        # Mock tweet text generation
        mock_generate_text.return_value = "بیست و سه تو"
        mock_get_url.return_value = "https://x.com/testuser/status/tweet123"

        # Set up mocks
        self.twitter_client.get_authenticated_user = Mock(return_value=mock_user)
        self.twitter_client.get_user_tweets = Mock(return_value=(mock_tweets, None))
        self.twitter_client.post_quote_tweet = Mock(
            return_value="https://x.com/testuser/status/new_tweet"
        )
        self.twitter_client.file_manager.store_counter = Mock()

        result = self.twitter_client.try_posting_tweet(23)

        self.assertTrue(result)
        self.twitter_client.get_authenticated_user.assert_called_once()
        self.twitter_client.get_user_tweets.assert_called_once_with("123456789")
        self.twitter_client.post_quote_tweet.assert_called_once_with(
            "بیست و سه تو", "tweet123", "testuser"
        )
        self.twitter_client.file_manager.store_counter.assert_called_once_with(23)

    @patch("bot.logger")
    def test_try_posting_tweet_no_user(self, mock_logger):
        """Test tweet posting when user authentication fails."""
        self.twitter_client.get_authenticated_user = Mock(return_value=None)

        result = self.twitter_client.try_posting_tweet(23)

        self.assertFalse(result)

    @patch("bot.logger")
    def test_try_posting_tweet_no_tweets(self, mock_logger):
        """Test tweet posting when no tweets found."""
        mock_user = Mock()
        mock_user.data.id = "123456789"

        self.twitter_client.get_authenticated_user = Mock(return_value=mock_user)
        self.twitter_client.get_user_tweets = Mock(return_value=(None, None))

        result = self.twitter_client.try_posting_tweet(23)

        self.assertFalse(result)
        self.assertTrue(mock_logger.error.called)

    @patch("bot.logger")
    def test_try_posting_tweet_no_quoted_tweets(self, mock_logger):
        """Test tweet posting when no quoted tweets found."""
        mock_user = Mock()
        mock_user.data.id = "123456789"
        mock_user.data.username = "testuser"

        # Mock tweets without quoted tweets
        mock_tweet = Mock()
        mock_tweet.referenced_tweets = [Mock(type="retweeted")]
        mock_tweet.text = "This is a test tweet"
        mock_tweet.created_at = datetime(2025, 9, 12, 15, 30)
        mock_tweet.id = "tweet123"

        mock_tweets = Mock()
        mock_tweets.data = [mock_tweet]

        self.twitter_client.get_authenticated_user = Mock(return_value=mock_user)
        self.twitter_client.get_user_tweets = Mock(return_value=(mock_tweets, None))

        result = self.twitter_client.try_posting_tweet(23)

        self.assertFalse(result)
        self.assertTrue(mock_logger.error.called)


class TestMainFunction(unittest.TestCase):
    """Test cases for the main function and integration scenarios."""

    @patch("bot.TwitterClient")
    @patch("bot.FileManager")
    @patch("bot.DateTimeUtil.get_counter_value_for_today")
    @patch("bot.logger")
    def test_main_no_tweet_needed(
        self, mock_logger, mock_get_counter, mock_file_manager, mock_twitter_client
    ):
        """Test main function when no tweet is needed."""
        # Mock file manager
        mock_fm_instance = Mock()
        mock_fm_instance.get_stored_counter.return_value = 100
        mock_file_manager.return_value = mock_fm_instance

        # Mock counter value
        mock_get_counter.return_value = 100

        main()

        mock_logger.info.assert_any_call(
            "✅ No tweet needed today. Stored counter is up to date."
        )
        mock_twitter_client.assert_not_called()

    @patch("bot.TwitterClient")
    @patch("bot.FileManager")
    @patch("bot.DateTimeUtil.get_counter_value_for_today")
    @patch("bot.DateTimeUtil.is_ci_environment")
    @patch("bot.logger")
    def test_main_tweet_needed_success(
        self,
        mock_logger,
        mock_is_ci,
        mock_get_counter,
        mock_file_manager,
        mock_twitter_client,
    ):
        """Test main function when tweet is needed and succeeds."""
        # Mock file manager
        mock_fm_instance = Mock()
        mock_fm_instance.get_stored_counter.return_value = 98
        mock_fm_instance.check_rate_limit_status.return_value = True
        mock_fm_instance.rate_limit_file_exists.return_value = False
        mock_file_manager.return_value = mock_fm_instance

        # Mock counter value
        mock_get_counter.return_value = 100

        # Mock CI environment
        mock_is_ci.return_value = False

        # Mock Twitter client
        mock_tc_instance = Mock()
        mock_tc_instance.try_posting_tweet.return_value = True
        mock_twitter_client.return_value = mock_tc_instance

        main()

        # Should process 2 tweets (99 and 100)
        self.assertEqual(mock_tc_instance.try_posting_tweet.call_count, 2)
        mock_tc_instance.try_posting_tweet.assert_any_call(99)
        mock_tc_instance.try_posting_tweet.assert_any_call(100)

    @patch("bot.TwitterClient")
    @patch("bot.FileManager")
    @patch("bot.DateTimeUtil.get_counter_value_for_today")
    @patch("bot.DateTimeUtil.is_ci_environment")
    @patch("bot.logger")
    def test_main_rate_limit_in_ci(
        self,
        mock_logger,
        mock_is_ci,
        mock_get_counter,
        mock_file_manager,
        mock_twitter_client,
    ):
        """Test main function when rate limited in CI environment."""
        # Mock file manager
        mock_fm_instance = Mock()
        mock_fm_instance.get_stored_counter.return_value = 98
        mock_fm_instance.check_rate_limit_status.return_value = False
        mock_fm_instance.rate_limit_file_exists.return_value = True
        mock_file_manager.return_value = mock_fm_instance

        # Mock counter value
        mock_get_counter.return_value = 100

        # Mock CI environment
        mock_is_ci.return_value = True

        main()

        mock_logger.error.assert_any_call(
            "❌ Rate limit active. Exiting in CI environment to allow scheduled retry."
        )
        mock_twitter_client.assert_called_once()  # TwitterClient created but not used

    @patch("bot.time.sleep")
    @patch("bot.TwitterClient")
    @patch("bot.FileManager")
    @patch("bot.DateTimeUtil.get_counter_value_for_today")
    @patch("bot.DateTimeUtil.is_ci_environment")
    @patch("bot.logger")
    def test_main_rate_limit_wait(
        self,
        mock_logger,
        mock_is_ci,
        mock_get_counter,
        mock_file_manager,
        mock_twitter_client,
        mock_sleep,
    ):
        """Test main function waits for rate limit in non-CI environment."""
        # Mock file manager
        mock_fm_instance = Mock()
        mock_fm_instance.get_stored_counter.return_value = 99
        # First call returns False (rate limited), second returns True
        mock_fm_instance.check_rate_limit_status.side_effect = [False, True]
        mock_fm_instance.rate_limit_file_exists.return_value = False
        mock_file_manager.return_value = mock_fm_instance

        # Mock counter value
        mock_get_counter.return_value = 100

        # Mock CI environment
        mock_is_ci.return_value = False

        # Mock Twitter client
        mock_tc_instance = Mock()
        mock_tc_instance.try_posting_tweet.return_value = True
        mock_twitter_client.return_value = mock_tc_instance

        main()

        # Should wait for rate limit
        mock_sleep.assert_called_once_with(Config.TWITTER_RATE_LIMIT_RESET_MINUTES * 60)
        mock_logger.info.assert_any_call("🔄 Checking rate limit status again...")

        # Should still post the tweet after waiting
        mock_tc_instance.try_posting_tweet.assert_called_once_with(100)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases."""

    @patch("bot.logger")
    def test_main_with_keyboard_interrupt(self, mock_logger):
        """Test main function handling of KeyboardInterrupt."""
        with patch(
            "bot.DateTimeUtil.get_counter_value_for_today",
            side_effect=KeyboardInterrupt,
        ):
            with self.assertRaises(KeyboardInterrupt):
                main()

    @patch("bot.logger")
    def test_main_with_unexpected_error(self, mock_logger):
        """Test main function handling of unexpected errors."""
        with patch(
            "bot.DateTimeUtil.get_counter_value_for_today",
            side_effect=Exception("Unexpected error"),
        ):
            with self.assertRaises(Exception):
                main()


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
