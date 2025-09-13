# SimJowBot

SimJowBot is an automated Twitter bot built with Python and Tweepy that posts daily Persian counting tweets. The bot features a modern object-oriented architecture with comprehensive testing, error handling, and CI/CD integration.

## Architecture

The bot follows a modern object-oriented design with clear separation of concerns:

- **`Config`**: Centralized configuration management with environment variables
- **`FileManager`**: Handles all file operations (counter storage, rate limit tracking)
- **`TwitterClient`**: Twitter API wrapper with enhanced error handling and rate limiting
- **`DateTimeUtil`**: Date calculations and CI environment detection utilities
- **`TwitterUtil`**: Tweet generation, analysis, and formatting utilities

## Dependencies

### Core Dependencies

The bot requires the following Python packages:

- **tweepy** (≥4.0): Twitter API v2 client library
- **python-dotenv**: Environment variable management
- **datetime**: Date and time handling (built-in)
- **os**: Operating system interface (built-in)
- **time**: Time-related functions (built-in)
- **logging**: Enhanced logging capabilities (built-in)
- **typing**: Type hints for better code quality (built-in)

### Development Dependencies

For testing and development:

- **unittest**: Testing framework (built-in)
- **pytest**: Modern test runner (recommended)
- **pytest-cov**: Test coverage reporting (optional)
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
   # Core dependencies
   pip install tweepy python-dotenv
   
   # Development dependencies (optional)
   pip install pytest pytest-cov
   ```

3. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   API_KEY=your_api_key_here
   API_KEY_SECRET=your_api_key_secret_here
   ACCESS_TOKEN=your_access_token_here
   ACCESS_TOKEN_SECRET=your_access_token_secret_here
   BEARER_TOKEN=your_bearer_token_here
   MAX_COUNTER_VALUE=your_max_counter_value_here
   MAX_COUNTER_TWEET_TEXT=your_secret_text_for_max_counter_here
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

6. **Run tests** to verify setup:
   ```bash
   # Run all tests
   python -m pytest tests/ -v
   
   # Run tests with coverage analysis (same as GitHub Actions)
   python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing --cov-report=xml --cov-fail-under=80
   ```

### GitHub Actions Deployment

#### Daily Tweet Workflow

1. **Fork the repository** to your GitHub account

2. **Configure GitHub Secrets**:
   Go to your repository settings → Secrets and variables → Actions, and add:
   - `API_KEY`
   - `API_KEY_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`
   - `MAX_COUNTER_VALUE` (required secret max counter value)
   - `MAX_COUNTER_TWEET_TEXT` (required secret text for max counter)

3. **Enable GitHub Actions**:
   - Go to the Actions tab in your repository
   - Enable workflows if prompted
   - The bot will automatically start running on the scheduled times

4. **Grant repository permissions**:
   - Ensure the workflow has write permissions to update `counter.txt`
   - This is configured in the workflow file under `permissions`

#### Continuous Integration Workflow

The repository includes an automated testing workflow (`tests.yml`).

The interactive HTML coverage report is automatically published to GitHub Pages and accessible at:

`https://m3y54m.github.io/SimJowBot/coverage/`

## Usage

### Manual Execution

Run the bot manually for testing:

```bash
# Run the bot
python bot.py

# Run with verbose logging (if implemented)
python bot.py --verbose
```

### Automated Execution

The bot runs automatically via GitHub Actions with the following schedule:
- **Primary run**: Daily at 19:17 (7:17 PM)
- **Retry attempts**: Every 17 minutes for up to 5 retries if the primary run fails

### Monitoring and Tools

1. **Check rate limits**:
   ```bash
   python tools/check_rate_limits.py
   ```

2. **Convert user IDs to usernames**:
   ```bash
   python tools/user_id_to_username.py 783214
   ```

3. **Run all tests**:
   ```bash
   python -m pytest tests/ -v
   ```

4. **Run specific test categories**:
   ```bash
   # Bot functionality tests only
   python -m pytest tests/test_bot.py -v
   
   # Persian numbers tests only
   python -m pytest tests/test_persian_numbers.py -v
   ```

## Persian Number Conversion

The bot includes a custom Persian number conversion module (`persian_numbers.py`).

### Example Conversions

```python
from persian_numbers import convert_to_persian_word

print(convert_to_persian_word(1))      # یک
print(convert_to_persian_word(21))     # بیست و یک
print(convert_to_persian_word(173))    # صد و هفتاد و سه
print(convert_to_persian_word(1234))   # هزار و دویست و سی و چهار
```

## Configuration

### Bot Configuration

The `Config` class centralizes all configuration:

```python
class Config:
    # Counter logic
    START_DATE = date(2025, 3, 18)     # Bot start date
    MAX_COUNTER_VALUE = int(os.environ.get("MAX_COUNTER_VALUE", str(ABS_COUNTING_LIMIT)))  # Secret max counter value
    
    # Rate limiting
    TWITTER_RATE_LIMIT_RESET_MINUTES = 15  # Rate limit reset time
    
    # Tweet processing
    MAX_TWEETS_TO_FETCH = 50           # Max tweets to fetch per request
    MAX_TWEET_PREVIEW_LENGTH = 100     # Tweet preview truncation
    
    # Special cases
    MAX_COUNTER_TWEET_TEXT = os.environ.get("MAX_COUNTER_TWEET_TEXT", "***")  # Secret text for max counter
```

### Counter Logic

The bot uses a date-based counter system:
- **Start date**: March 18, 2025
- **Starting value**: 1
- **Increment**: +1 per day
- **Maximum**: MAX_COUNTER_VALUE (reaches maximum after MAX_COUNTER_VALUE days)

### Scheduling

GitHub Actions workflow runs:
- **Main schedule**: `17 19 * * *` (19:17 daily)
- **Retry schedule**: Every 17 minutes for 9 attempts
- **Manual trigger**: Can be triggered manually via GitHub Actions UI

## Testing

The project includes comprehensive test suites for both the Persian number conversion and the main bot functionality:

### All Tests
```bash
# Run all tests in the project (58 total test cases)
python -m pytest tests/ -v

# Run all tests with coverage (if coverage is installed)
python -m pytest tests/ --cov=. --cov-report=html

# Run tests in parallel (if pytest-xdist is installed)
python -m pytest tests/ -n auto
```

### Bot Functionality Tests
```bash
# Run comprehensive bot tests (52 test cases)
python -m pytest tests/test_bot.py -v

# Run specific test class
python -m pytest tests/test_bot.py::TestTwitterClient -v

# Run specific test method
python -m pytest tests/test_bot.py::TestConfig::test_config_default_values -v
```

### Persian Numbers Tests
```bash
# Run Persian number conversion tests (6 test cases)
python -m pytest tests/test_persian_numbers.py -v

# Run interactively (legacy mode)
python tests/test_persian_numbers.py
# Choose option 3 for interactive mode
# Choose option 4 to include performance tests
```

### Prerequisites for Testing

Install testing dependencies:
```bash
# Required for running tests
pip install pytest

# Optional: For test coverage reports
pip install pytest-cov

# Optional: For better test output formatting
pip install pytest-sugar

# Optional: For parallel test execution
pip install pytest-xdist

# Optional: For watch mode during development
pip install pytest-watch
```

### Development Workflow

For development workflow:

```bash
# Watch mode (if pytest-watch is installed)
pip install pytest-watch
ptw tests/

# Run tests on file changes
python -m pytest tests/ --looponfail

# Run with maximum verbosity for debugging
python -m pytest tests/ -vvv

# Run only failed tests from last run
python -m pytest tests/ --lf

# Generate HTML coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

## Troubleshooting

### Enable Debug Logging

```python
import logging
logging.getLogger('bot').setLevel(logging.DEBUG)
```

### Test Individual Components

```bash
# Test only configuration
python -m pytest tests/test_bot.py::TestConfig -v

# Test only file operations
python -m pytest tests/test_bot.py::TestFileManager -v

# Test only Twitter client
python -m pytest tests/test_bot.py::TestTwitterClient -v
```

### Manual Testing

```python
from bot import DateTimeUtil, Config, FileManager

# Check current counter value
print(f"Expected counter: {DateTimeUtil.get_counter_value_for_today()}")

# Check stored counter
fm = FileManager()
print(f"Stored counter: {fm.get_stored_counter()}")

# Check CI environment
print(f"CI Environment: {DateTimeUtil.is_ci_environment()}")
```

## License

This project is open source and licensed under the MIT License. See the [LICENSE](./LICENSE) file for details. Please ensure you comply with Twitter's Terms of Service and API usage policies when using this bot.
