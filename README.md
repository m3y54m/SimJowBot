# SimJowBot

SimJowBot is an automated Twitter bot built with Python and Tweepy that posts daily Persian counting tweets. It tracks a counter starting from March 18, 2025, and automatically posts quote tweets with Persian number words.

## Features

- **Automated Daily Posting**: Posts tweets daily at scheduled times using GitHub Actions
- **Persian Number Conversion**: Converts numbers to Persian words (e.g., 174 → "صد و هفتاد و چهار تو")
- **Quote Tweet System**: Automatically finds and quotes the most recent quoted tweet from the authenticated user
- **Rate Limit Handling**: Smart rate limit management with automatic retry scheduling
- **Error Recovery**: Robust error handling and recovery mechanisms
- **CI/CD Integration**: Fully automated deployment via GitHub Actions workflows

## How It Works

1. **Daily Schedule**: The bot runs automatically via GitHub Actions at 19:17 (7 PM) daily, with retry attempts every 17 minutes if needed
2. **Counter Logic**: Calculates the expected counter value based on days elapsed since March 18, 2025 (starting at 1)
3. **Tweet Discovery**: Fetches recent tweets from the authenticated user and identifies quoted tweets
4. **Persian Conversion**: Converts the current counter to Persian words using a custom algorithm
5. **Quote Tweet**: Posts a new quote tweet with the Persian number followed by "تو"
6. **State Management**: Updates and commits the counter state back to the repository

## Project Structure

```
SimJowBot/
├── bot.py                          # Main bot script
├── persian_numbers.py              # Persian number to word conversion module
├── counter.txt                     # Current counter state (managed by bot)
├── tools/                          # Utility scripts
│   ├── check_rate_limits.py        # Rate limit monitoring tool
│   ├── get_custom_user_access_token.py  # OAuth token generation helper
│   └── user_id_to_username.py      # User ID to username converter
├── tests/                          # Test suite
│   ├── test_persian_numbers.py     # Comprehensive testing for Persian numbers
│   ├── generate_lut.py             # Lookup table generator
│   └── lut.txt                     # Reference lookup table for testing
└── .github/workflows/
    └── tweet.yml                   # GitHub Actions workflow for automation
```

## Dependencies

The bot requires the following Python packages:

- **tweepy** (≥4.0): Twitter API v2 client library
- **python-dotenv**: Environment variable management
- **datetime**: Date and time handling (built-in)
- **os**: Operating system interface (built-in)
- **time**: Time-related functions (built-in)

For testing and development:
- **unittest**: Testing framework (built-in)
- **persian-tools**: Reference library for test validation (optional)

## Setup and Installation

### Prerequisites

1. **Twitter Developer Account**: Apply for a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com)
2. **Twitter API v2 Access**: Create a new app and generate API credentials
3. **Python 3.12+**: Ensure you have Python 3.12 or later installed
4. **GitHub Account**: For automated deployment (if using GitHub Actions)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/m3y54m/SimJowBot.git
   cd SimJowBot
   ```

2. **Install dependencies**:
   ```bash
   pip install tweepy python-dotenv
   ```

3. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   API_KEY=your_api_key_here
   API_KEY_SECRET=your_api_key_secret_here
   ACCESS_TOKEN=your_access_token_here
   ACCESS_TOKEN_SECRET=your_access_token_secret_here
   BEARER_TOKEN=your_bearer_token_here
   ```

4. **Generate OAuth tokens** (if needed):
   ```bash
   python tools/get_custom_user_access_token.py
   ```

5. **Initialize counter** (optional):
   Create `counter.txt` with your starting value:
   ```bash
   echo "1" > counter.txt
   ```

### GitHub Actions Deployment

1. **Fork the repository** to your GitHub account

2. **Configure GitHub Secrets**:
   Go to your repository settings → Secrets and variables → Actions, and add:
   - `API_KEY`
   - `API_KEY_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`

3. **Enable GitHub Actions**:
   - Go to the Actions tab in your repository
   - Enable workflows if prompted
   - The bot will automatically start running on the scheduled times

4. **Grant repository permissions**:
   - Ensure the workflow has write permissions to update `counter.txt`
   - This is configured in the workflow file under `permissions`

## Usage

### Manual Execution

Run the bot manually for testing:

```bash
python bot.py
```

### Automated Execution

The bot runs automatically via GitHub Actions with the following schedule:
- **Primary run**: Daily at 19:17 (7:17 PM)
- **Retry attempts**: Every 17 minutes for up to 9 retries if the primary run fails

### Monitoring and Tools

1. **Check rate limits**:
   ```bash
   python tools/check_rate_limits.py
   ```

2. **Convert user IDs to usernames**:
   ```bash
   python tools/user_id_to_username.py 783214
   ```

3. **Run tests**:
   ```bash
   python tests/test_persian_numbers.py
   ```

## Persian Number Conversion

The bot includes a custom Persian number conversion module (`persian_numbers.py`) that:

- **Supports numbers**: -999,999 to +999,999
- **Algorithmic conversion**: Uses lookup table with algorithmic generation
- **Proper grammar**: Includes correct Persian grammar with "و" (and) connectors
- **No external dependencies**: Self-contained with embedded lookup table
- **High performance**: Optimized for fast conversion (< 1ms per conversion)

### Example Conversions

```python
from persian_numbers import convert_to_persian_word

print(convert_to_persian_word(1))      # یک
print(convert_to_persian_word(21))     # بیست و یک
print(convert_to_persian_word(173))    # صد و هفتاد و سه
print(convert_to_persian_word(1234))   # هزار و دویست و سی و چهار
```

## Configuration

### Counter Logic

The bot uses a date-based counter system:
- **Start date**: March 18, 2025
- **Starting value**: 1
- **Increment**: +1 per day
- **Maximum**: 1000 (reaches maximum after 1000 days)

### Rate Limiting

The bot implements smart rate limiting:
- **Twitter API limits**: 75 requests per 15 minutes (free tier)
- **Reset tracking**: Automatically tracks when limits reset
- **Retry logic**: Waits for rate limits to reset before retrying
- **CI-friendly**: Fails fast in CI environments for scheduled retries

### Scheduling

GitHub Actions workflow runs:
- **Main schedule**: `17 19 * * *` (19:17 daily)
- **Retry schedule**: Every 17 minutes for 9 attempts
- **Manual trigger**: Can be triggered manually via GitHub Actions UI

## Error Handling

The bot includes comprehensive error handling:

1. **Rate limit errors**: Automatic detection and scheduling for retry
2. **API errors**: Graceful handling of Twitter API issues
3. **File I/O errors**: Robust file handling with error recovery
4. **Authentication errors**: Clear error messages for credential issues
5. **Network errors**: Retry logic for temporary network issues

## Testing

### Running Tests

The project includes a comprehensive test suite:

```bash
# Run all tests
python tests/test_persian_numbers.py

# Interactive testing
python tests/test_persian_numbers.py
# Choose option 3 for interactive mode

# Performance testing
python tests/test_persian_numbers.py
# Choose option 4 to include performance tests
```

### Test Coverage

- **Unit tests**: Validates against reference lookup table (1-1000)
- **Edge cases**: Tests boundary values and special cases
- **Performance tests**: Ensures conversion speed < 1ms per conversion
- **Error handling**: Tests out-of-range number handling
- **Negative numbers**: Validates negative number conversion

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes**
4. **Run tests**: `python tests/test_persian_numbers.py`
5. **Commit changes**: `git commit -am 'Add new feature'`
6. **Push to branch**: `git push origin feature/new-feature`
7. **Create a Pull Request**

## License

This project is open source. Please ensure you comply with Twitter's Terms of Service and API usage policies when using this bot.

## Troubleshooting

### Common Issues

1. **Rate limit errors**:
   - Wait 15 minutes between manual runs
   - Check `rate_limit_failure.txt` for last failure time
   - Consider upgrading to paid Twitter API plan

2. **Authentication errors**:
   - Verify all API credentials in `.env` file
   - Ensure tokens have appropriate permissions
   - Run `tools/get_custom_user_access_token.py` to regenerate tokens

3. **GitHub Actions not running**:
   - Check repository permissions
   - Verify GitHub Secrets are properly configured
   - Ensure workflows are enabled in repository settings

4. **Counter out of sync**:
   - Manually update `counter.txt` with correct value
   - The bot will automatically catch up on next run

### Getting Help

- Check the GitHub Issues for known problems
- Review the Twitter API documentation for API-related issues
- Test components individually using the tools in the `tools/` directory

## API Rate Limits

**Twitter API Free Tier Limits**:
- Get user tweets: 75 requests per 15 minutes
- Post tweets: 25 posts per 24 hours
- Most endpoints reset every 15 minutes

The bot is designed to work within these limits with automatic retry scheduling.
