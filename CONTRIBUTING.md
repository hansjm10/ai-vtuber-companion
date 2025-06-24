# Contributing to AI VTuber Companion

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ai-vtuber-companion.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/hansjm10/ai-vtuber-companion.git
cd ai-vtuber-companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run setup
python setup.py
```

## Code Style

- Follow PEP 8
- Use Black for formatting: `black src/`
- Use Ruff for linting: `ruff check src/`
- Add type hints where possible
- Write docstrings for all functions and classes

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Run tests with: `pytest tests/ -v`

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the ROADMAP.md if you're implementing a planned feature
3. Ensure all tests pass and linting is clean
4. Request review from maintainers

## Areas for Contribution

- [ ] Implement new AI models support
- [ ] Add new TTS/STT engines
- [ ] Improve performance optimizations
- [ ] Create frontend dashboard components
- [ ] Add new personality traits
- [ ] Write documentation
- [ ] Create unit tests
- [ ] Report and fix bugs

## Questions?

Feel free to open an issue for any questions or join our Discord server (coming soon).