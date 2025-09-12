#!/usr/bin/env python3
"""
Twitter User ID to Username Converter

This script converts Twitter user_id numbers to usernames using the Twitter API v2.
It can handle single user IDs or batch lookups for multiple user IDs.

Usage:
    python user_id_to_username.py <user_id>
    python user_id_to_username.py <user_id1> <user_id2> <user_id3> ...

Examples:
    python user_id_to_username.py 783214
    python user_id_to_username.py 783214 25073877 44196397

Requirements:
    - Twitter API credentials in .env file
    - tweepy library
    - python-dotenv library
"""

import tweepy
import os
import sys
from dotenv import load_dotenv

def setup_twitter_client():
    """Setup and return authenticated Twitter API client"""
    # Load environment variables from .env file
    load_dotenv()

    # Your Twitter API credentials
    API_KEY = os.environ.get("API_KEY")
    API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
    BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

    # Check if credentials are available
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
        print("Error: Missing Twitter API credentials in .env file")
        print("Required variables: API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN")
        sys.exit(1)

    # Authenticate with the Twitter API
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    return client

def convert_user_ids_to_usernames(client, user_ids):
    """
    Convert a list of user IDs to usernames
    
    Args:
        client: Authenticated Tweepy client
        user_ids: List of user ID strings or integers
        
    Returns:
        Dictionary mapping user_id -> username
    """
    results = {}
    
    try:
        # Convert all user_ids to strings
        user_ids_str = [str(uid) for uid in user_ids]
        
        # Get users by IDs (Twitter API allows up to 100 user IDs per request)
        # For large batches, we'd need to chunk them, but for typical usage this should be fine
        if len(user_ids_str) > 100:
            print(f"Warning: {len(user_ids_str)} user IDs provided. Processing first 100 only.")
            user_ids_str = user_ids_str[:100]
        
        response = client.get_users(ids=user_ids_str)
        
        if response.data:
            for user in response.data:
                results[user.id] = user.username
        
        # Check for users that weren't found
        found_ids = set(results.keys())
        requested_ids = set(user_ids_str)
        missing_ids = requested_ids - found_ids
        
        if missing_ids:
            for missing_id in missing_ids:
                results[missing_id] = "NOT_FOUND"
                
    except tweepy.Forbidden as e:
        print(f"Error: Access forbidden. Check your API credentials and permissions.")
        print(f"Details: {e}")
        return None
    except tweepy.TooManyRequests as e:
        print(f"Error: Rate limit exceeded. Please wait before trying again.")
        print(f"Details: {e}")
        return None
    except tweepy.NotFound as e:
        print(f"Error: One or more user IDs not found.")
        print(f"Details: {e}")
        # Still return partial results if available
        return results
    except Exception as e:
        print(f"Error occurred while fetching user information: {e}")
        return None
    
    return results

def main():
    """Main function to handle command line arguments and execute conversion"""
    
    if len(sys.argv) < 2:
        print("Usage: python user_id_to_username.py <user_id> [user_id2] [user_id3] ...")
        print("\nExamples:")
        print("  python user_id_to_username.py 783214")
        print("  python user_id_to_username.py 783214 25073877 44196397")
        sys.exit(1)
    
    # Get user IDs from command line arguments
    user_ids = sys.argv[1:]
    
    # Validate that all arguments are numeric
    for user_id in user_ids:
        if not user_id.isdigit():
            print(f"Error: '{user_id}' is not a valid user ID (must be numeric)")
            sys.exit(1)
    
    print(f"Converting {len(user_ids)} user ID(s) to username(s)...")
    
    # Setup Twitter client
    client = setup_twitter_client()
    
    # Convert user IDs to usernames
    results = convert_user_ids_to_usernames(client, user_ids)
    
    if results is None:
        print("Failed to convert user IDs due to API error.")
        sys.exit(1)
    
    # Display results
    print("\nResults:")
    print("=" * 50)
    
    for user_id in user_ids:
        username = results.get(user_id, "ERROR")
        if username == "NOT_FOUND":
            print(f"User ID: {user_id:15} -> Username: NOT FOUND")
        elif username == "ERROR":
            print(f"User ID: {user_id:15} -> Username: ERROR")
        else:
            print(f"User ID: {user_id:15} -> Username: @{username}")
    
    print("=" * 50)
    
    # Summary
    successful_conversions = sum(1 for username in results.values() if username not in ["NOT_FOUND", "ERROR"])
    print(f"Successfully converted {successful_conversions} out of {len(user_ids)} user ID(s)")

if __name__ == "__main__":
    main()