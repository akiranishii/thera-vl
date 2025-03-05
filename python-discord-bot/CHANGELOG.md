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
- Detailed documentation in README files
  - Updated main README.md with new setup instructions
  - Added README_TESTS.md with testing documentation

### Changed
- Updated `llm_client.py` to properly initialize providers dictionary
- Improved error handling in LLM client
- Enhanced configuration loading in `config.py`
- Better logging throughout the application

### Fixed
- Fixed 'LLMClient' object has no attribute 'providers' error
- Improved error handling when API keys are missing
- Added graceful fallback to mock implementations when needed 