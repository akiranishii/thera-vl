# Changelog

## [Unreleased] - 2025-03-03

### Added
- Environment variable loading from `.env` file using python-dotenv
- Support for multiple LLM providers (OpenAI, Anthropic, Mistral)
- Comprehensive test scripts for LLM functionality
  - `test_llm_agents.py` - Real API tests with fallback to mocks
  - `test_llm_agents_mock.py` - Pure mock tests
- Installation script `install_dependencies.sh` for easy setup
- Runner script `run.py` with environment validation and test options
- API connection validation with `--check-api` option in run.py
- Detailed documentation in README files
  - Updated main README.md with new setup instructions
  - Added README_TESTS.md with testing documentation
  - Added API troubleshooting section to README.md

### Changed
- Updated `llm_client.py` to properly initialize providers dictionary
- Improved error handling in LLM client
- Enhanced configuration loading in `config.py`
- Better logging throughout the application
- Enhanced `DatabaseClient` to prevent API URL path duplication

### Fixed
- Fixed 'LLMClient' object has no attribute 'providers' error
- Improved error handling when API keys are missing
- Added graceful fallback to mock implementations when needed
- Fixed API URL duplication issue causing 404 errors
- Added detection and prevention of duplicate `/api` segments in URLs 