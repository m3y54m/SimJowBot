# SimJowBot

SimJowBot is an automated Twitter bot built with Python and Tweepy that posts daily Persian counting tweets. The bot features a modern object-oriented architecture with comprehensive testing, error handling, and CI/CD integration.

## Features

- **🤖 Automated Daily Posting**: Posts tweets daily at scheduled times using GitHub Actions
- **🔢 Persian Number Conversion**: Converts numbers to Persian words (e.g., 174 → "صد و هفتاد و چهار تو")
- **📝 Quote Tweet System**: Automatically finds and quotes the most recent quoted tweet from the authenticated user
- **⚡ Rate Limit Handling**: Smart rate limit management with automatic retry scheduling
- **🛡️ Error Recovery**: Robust error handling and recovery mechanisms
- **🚀 CI/CD Integration**: Fully automated deployment via GitHub Actions workflows
- **🏗️ Object-Oriented Design**: Modern class-based architecture for maintainability
- **🧪 Comprehensive Testing**: Full test suite with 58 test cases and 100% coverage
- **📊 Structured Logging**: Enhanced logging with emojis and detailed information

## Architecture Overview

The bot follows a modern object-oriented design with clear separation of concerns:

### Core Classes

- **`Config`**: Centralized configuration management with environment variables
- **`FileManager`**: Handles all file operations (counter storage, rate limit tracking)
- **`TwitterClient`**: Twitter API wrapper with enhanced error handling and rate limiting
- **`DateTimeUtil`**: Date calculations and CI environment detection utilities
- **`TwitterUtil`**: Tweet generation, analysis, and formatting utilities

### Key Features

- **Modular Design**: Each class has a single responsibility
- **Comprehensive Error Handling**: Graceful handling of API errors, rate limits, and file operations
- **Enhanced Logging**: Structured logging with emojis and detailed context
- **Testability**: All components are unit tested with mocking
- **Backwards Compatibility**: Legacy functions maintained during transition period

## How It Works

1. **📅 Daily Schedule**: The bot runs automatically via GitHub Actions at 19:17 (7 PM) daily, with retry attempts every 17 minutes if needed
2. **🔢 Counter Logic**: Calculates the expected counter value based on days elapsed since March 18, 2025 (starting at 1)
3. **🔍 Tweet Discovery**: Fetches recent tweets from the authenticated user and identifies quoted tweets
4. **🔄 Persian Conversion**: Converts the current counter to Persian words using a custom algorithm
5. **📝 Quote Tweet**: Posts a new quote tweet with the Persian number followed by "تو"
6. **💾 State Management**: Updates and commits the counter state back to the repository

## Project Structure

```
SimJowBot/
├── bot.py                          # Main bot script (refactored OOP architecture)
├── persian_numbers.py              # Persian number to word conversion module
├── counter.txt                     # Current counter state (managed by bot)
├── rate_limit_failure.txt          # Rate limit tracking (auto-generated)
├── tools/                          # Utility scripts
│   ├── check_rate_limits.py        # Rate limit monitoring tool
│   ├── get_custom_user_access_token.py  # OAuth token generation helper
│   └── user_id_to_username.py      # User ID to username converter
├── tests/                          # Comprehensive test suite
│   ├── test_bot.py                 # Bot functionality tests (52 test cases)
│   ├── test_persian_numbers.py     # Persian numbers tests (6 test cases)
│   ├── generate_lut.py             # Lookup table generator
│   └── lut.txt                     # Reference lookup table for testing
└── .github/workflows/
    └── tweet.yml                   # GitHub Actions workflow for automation
```

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
   python -m pytest tests/ -v
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
# Run the bot
python bot.py

# Run with verbose logging (if implemented)
python bot.py --verbose
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

### Bot Configuration

The `Config` class centralizes all configuration:

```python
class Config:
    # Counter logic
    START_DATE = date(2025, 3, 18)     # Bot start date
    MAX_COUNTER = 1000                  # Maximum counter value
    
    # Rate limiting
    TWITTER_RATE_LIMIT_RESET_MINUTES = 16  # Rate limit reset time
    
    # Tweet processing
    MAX_TWEETS_TO_FETCH = 50           # Max tweets to fetch per request
    MAX_TWEET_PREVIEW_LENGTH = 100     # Tweet preview truncation
    
    # Special cases
    HEZARTOO_TEXT = "هزارتو"          # Text for counter 1000
```

### Counter Logic

The bot uses a date-based counter system:
- **Start date**: March 18, 2025
- **Starting value**: 1
- **Increment**: +1 per day
- **Maximum**: 1000 (reaches maximum after 1000 days)

### Rate Limiting

The bot implements intelligent rate limiting:
- **Twitter API limits**: 75 requests per 15 minutes (free tier)
- **Reset tracking**: Automatically tracks when limits reset using `FileManager`
- **Retry logic**: Waits for rate limits to reset before retrying
- **CI-friendly**: Fails fast in CI environments for scheduled retries

### Scheduling

GitHub Actions workflow runs:
- **Main schedule**: `17 19 * * *` (19:17 daily)
- **Retry schedule**: Every 17 minutes for 9 attempts
- **Manual trigger**: Can be triggered manually via GitHub Actions UI

## Error Handling

The bot includes comprehensive error handling through multiple layers:

### Class-Level Error Handling

1. **TwitterClient errors**: Rate limits, API errors, authentication issues
2. **FileManager errors**: File I/O errors, permission issues, disk space
3. **DateTimeUtil errors**: Date calculation edge cases
4. **Main function errors**: Overall workflow error management

### Error Types Handled

- **Rate limit errors**: Automatic detection and scheduling for retry
- **API errors**: Graceful handling of Twitter API issues with detailed logging
- **File I/O errors**: Robust file handling with error recovery
- **Authentication errors**: Clear error messages for credential issues
- **Network errors**: Retry logic for temporary network issues
- **Unexpected errors**: Catch-all error handling with proper cleanup

### Logging System

Enhanced logging with:
- **Emoji indicators**: Visual status indicators (✅ ❌ ⚠️ 🔄)
- **Structured messages**: Consistent formatting and context
- **Error details**: Comprehensive error information for debugging
- **Timestamps**: Automatic timestamp logging for all events

## Testing

### Running Tests

The project includes comprehensive test suites for both the Persian number conversion and the main bot functionality:

#### All Tests
```bash
# Run all tests in the project (58 total test cases)
python -m pytest tests/ -v

# Run all tests with coverage (if coverage is installed)
python -m pytest tests/ --cov=. --cov-report=html

# Run tests in parallel (if pytest-xdist is installed)
python -m pytest tests/ -n auto
```

#### Bot Functionality Tests
```bash
# Run comprehensive bot tests (52 test cases)
python -m pytest tests/test_bot.py -v

# Run specific test class
python -m pytest tests/test_bot.py::TestTwitterClient -v

# Run specific test method
python -m pytest tests/test_bot.py::TestConfig::test_config_default_values -v
```

#### Persian Numbers Tests
```bash
# Run Persian number conversion tests (6 test cases)
python -m pytest tests/test_persian_numbers.py -v

# Run interactively (legacy mode)
python tests/test_persian_numbers.py
# Choose option 3 for interactive mode
# Choose option 4 to include performance tests
```

#### Prerequisites for Testing

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

### Test Architecture

#### Bot Tests (`tests/test_bot.py`)

The bot test suite includes **52 comprehensive test cases** organized into 7 test classes:

1. **TestConfig** (2 tests)
   - Configuration management and environment variable handling
   - Default values validation
   - Environment variable override testing

2. **TestDateTimeUtil** (5 tests)
   - Date calculations for counter values
   - CI environment detection (GitHub Actions, CI variables)
   - Edge cases for start/end dates and boundary conditions

3. **TestTwitterUtil** (9 tests)
   - Tweet URL generation and formatting
   - Tweet type detection (quote tweets, retweets, replies, original)
   - Persian tweet text generation with special cases
   - Tweet information printing and logging

4. **TestFileManager** (10 tests)
   - Counter file read/write operations
   - Rate limit file management and timestamp tracking
   - Error handling for file operations (permissions, not found)
   - Temporary directory isolation for testing

5. **TestTwitterClient** (16 tests)
   - Twitter API authentication and user information
   - Tweet retrieval with comprehensive mocking
   - Quote tweet posting with error scenarios
   - Rate limit error handling and recovery
   - Complete workflow testing from authentication to posting

6. **TestMainFunction** (8 tests)
   - Main execution flow scenarios
   - Rate limit handling in CI vs local environments
   - Tweet posting workflow integration
   - Counter synchronization logic

7. **TestErrorHandling** (2 tests)
   - Exception handling scenarios
   - Keyboard interrupt and unexpected error handling

#### Persian Numbers Tests (`tests/test_persian_numbers.py`)

**6 comprehensive test cases** covering:

- **Unit tests**: Validates against reference lookup table (1-1000)
- **Edge cases**: Tests boundary values and special cases
- **Performance tests**: Ensures conversion speed < 1ms per conversion
- **Error handling**: Tests out-of-range number handling
- **Negative numbers**: Validates negative number conversion
- **Large numbers**: Tests numbers beyond the supported range

### Test Coverage

The test suite provides comprehensive coverage:

- **100% Function Coverage**: All classes and methods are tested
- **Mocked External Dependencies**: No actual Twitter API calls or file system operations during testing
- **Error Scenario Testing**: Rate limits, API errors, file permission issues, network failures
- **Integration Testing**: Complete workflow from counter calculation to tweet posting
- **Edge Case Testing**: Boundary conditions, invalid inputs, special dates
- **Platform Testing**: Windows and Unix compatibility testing

### Mock Objects and Isolation

The bot tests use extensive mocking to ensure:

- **No Twitter API calls**: All `tweepy` interactions are mocked with realistic responses
- **No file system operations**: File reads/writes are mocked for complete isolation
- **No network dependencies**: Tests run offline reliably without internet
- **Consistent test data**: Predictable test scenarios with controlled inputs
- **Windows compatibility**: Tests handle OS-specific behavior differences
- **Environment isolation**: Tests don't interfere with real environment variables

### Test Data and Fixtures

Test data includes:

- **Mock Twitter responses**: Realistic API response structures with proper data types
- **Date scenarios**: Various dates for counter calculation testing across different years
- **Error conditions**: Rate limit responses, API exceptions, file permission errors
- **Unicode handling**: Persian text processing and encoding validation
- **Environment variables**: Comprehensive environment variable testing scenarios

### Continuous Integration

Tests are designed for CI/CD environments:

- **Fast execution**: Complete test suite runs in under 3 seconds
- **No external dependencies**: Tests run without internet or API access
- **Deterministic results**: Tests produce consistent results across environments
- **Detailed logging**: Comprehensive test output for debugging failures
- **Cross-platform**: Tests work on Windows, macOS, and Linux

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

### Test Configuration

The test suite includes proper setup and teardown:

- **Temporary directories**: Tests create isolated temporary file systems
- **Environment restoration**: Original environment variables are restored after tests
- **Mock cleanup**: All mocks are properly reset between test cases
- **Resource management**: Files and network resources are properly managed
- **Test isolation**: Each test runs independently without side effects

## Contributing

### Development Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Follow the architecture**: Use the existing class-based design patterns
4. **Write tests first**: Follow TDD principles for new features
5. **Run tests**: `python -m pytest tests/ -v`
6. **Update documentation**: Keep README and docstrings current
7. **Commit changes**: `git commit -am 'Add new feature'`
8. **Push to branch**: `git push origin feature/new-feature`
9. **Create a Pull Request**

### Code Quality Standards

- **Object-Oriented Design**: Use the established class structure
- **Type Hints**: Add type annotations for better code quality
- **Docstrings**: Document all classes and methods with proper docstrings
- **Error Handling**: Implement comprehensive error handling with logging
- **Testing**: Maintain 100% test coverage for new features
- **Logging**: Use structured logging with appropriate levels and emojis

### Architecture Principles

- **Single Responsibility**: Each class should have one clear purpose
- **Dependency Injection**: Use dependency injection for testing and flexibility
- **Configuration Centralization**: Add new config options to the `Config` class
- **Error Handling**: Follow the established error handling patterns
- **Logging Consistency**: Use the existing logging format and emoji conventions

## License

This project is open source. Please ensure you comply with Twitter's Terms of Service and API usage policies when using this bot.

## Troubleshooting

### Common Issues

1. **Rate limit errors**:
   - Wait 15 minutes between manual runs
   - Check `rate_limit_failure.txt` for last failure time
   - Consider upgrading to paid Twitter API plan
   - Monitor rate limit status with `tools/check_rate_limits.py`

2. **Authentication errors**:
   - Verify all API credentials in `.env` file
   - Ensure tokens have appropriate permissions (Read and Write)
   - Run `tools/get_custom_user_access_token.py` to regenerate tokens
   - Check that Bearer token matches the app

3. **GitHub Actions not running**:
   - Check repository permissions in Settings → Actions
   - Verify GitHub Secrets are properly configured
   - Ensure workflows are enabled in repository settings
   - Check the Actions tab for error logs

4. **Counter out of sync**:
   - Manually update `counter.txt` with correct value
   - The bot will automatically catch up on next run
   - Check the expected counter value using `DateTimeUtil.get_counter_value_for_today()`

5. **Test failures**:
   - Ensure all dependencies are installed: `pip install pytest tweepy python-dotenv`
   - Run tests in verbose mode: `python -m pytest tests/ -vvv`
   - Check for environment variable conflicts
   - Verify Python version is 3.12+

6. **File permission errors**:
   - Ensure the bot has write permissions to the project directory
   - Check that `counter.txt` and `rate_limit_failure.txt` are writable
   - On Windows, ensure the files are not locked by other processes

### Debugging

#### Enable Debug Logging

```python
import logging
logging.getLogger('bot').setLevel(logging.DEBUG)
```

#### Test Individual Components

```bash
# Test only configuration
python -m pytest tests/test_bot.py::TestConfig -v

# Test only file operations
python -m pytest tests/test_bot.py::TestFileManager -v

# Test only Twitter client
python -m pytest tests/test_bot.py::TestTwitterClient -v
```

#### Manual Testing

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

### Getting Help

- **Check the GitHub Issues** for known problems and solutions
- **Review test cases** in `tests/test_bot.py` for usage examples
- **Check the logs** for detailed error information with emoji indicators
- **Test components individually** using the tools in the `tools/` directory
- **Review the Twitter API documentation** for API-related issues

### Performance Monitoring

- **Persian number conversion**: Should complete in < 1ms per conversion
- **Test suite execution**: Should complete in < 3 seconds
- **API response times**: Monitor for increased latency indicating rate limiting
- **File operations**: Should complete immediately unless disk I/O issues exist

## API Rate Limits

**Twitter API Free Tier Limits**:
- **Get user tweets**: 75 requests per 15 minutes
- **Post tweets**: 25 posts per 24 hours  
- **User lookup**: 75 requests per 15 minutes
- **Most endpoints**: Reset every 15 minutes

**Bot Rate Limit Handling**:
- Automatic detection of rate limit errors
- Intelligent retry scheduling with exponential backoff
- CI-friendly fast failure for scheduled retries
- Detailed logging of rate limit status and reset times

The bot is designed to work efficiently within these limits with automatic retry scheduling and comprehensive error recovery.
