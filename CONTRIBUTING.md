# Contributing to Secure Sandbox

Thank you for your interest in contributing to Secure Sandbox! This document provides guidelines and instructions for contributing.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourname/secure-sandbox.git
cd secure-sandbox
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This will install:
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `black` - Code formatter
- `mypy` - Type checker
- `flake8` - Linter

## Project Structure

```
secure-sandbox/
├── src/
│   └── secure_sandbox/      # Main package
│       ├── __init__.py
│       ├── core.py
│       ├── whitelist.py
│       ├── exceptions.py
│       └── cli.py
├── tests/                   # Test suite
│   ├── test_basic.py
│   ├── test_security.py
│   └── test_config.py
├── docs/                    # Documentation
│   └── README_CN.md
├── examples/                # Usage examples
│   ├── basic_usage.py
│   └── custom_config.py
├── README.md                # English documentation
├── CONTRIBUTING.md          # This file
├── setup.py                 # Setup script
└── pyproject.toml           # Modern config
```

## Coding Standards

### Code Style

We use `black` for code formatting:

```bash
# Format code
black src/ tests/ examples/

# Check formatting
black --check src/ tests/ examples/
```

### Type Hints

We encourage using type hints:

```python
def safe_execute(
    code_str: str,
    max_gas: int = 10000,
    config: Optional[SecurityConfig] = None
) -> Dict[str, Any]:
    ...
```

### Linting

Use `flake8` for linting:

```bash
flake8 src/ tests/ examples/
```

### Type Checking

Use `mypy` for type checking:

```bash
mypy src/
```

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/secure_sandbox --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run specific test
pytest tests/test_basic.py::test_safe_execution
```

### Writing Tests

Follow pytest conventions:

```python
import pytest
from secure_sandbox import safe_execute, GasLimitExceeded

def test_infinite_loop():
    """Test that infinite loops are caught by Gas mechanism"""
    code = """
    i = 0
    while True:
        i += 1
    """
    
    with pytest.raises(GasLimitExceeded):
        safe_execute(code, max_gas=10)
```

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow coding standards
- Add tests for new features
- Update documentation if needed

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/

# Run linter
flake8 src/ tests/

# Run type checker
mypy src/

# Run tests
pytest tests/
```

### 4. Commit Changes

Write clear commit messages:

```bash
git add .
git commit -m "Add feature: custom module whitelist support"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create Pull Request on GitHub.

## Adding New Features

### Security Features

When adding security features:

1. **Document the threat**: What attack does it prevent?
2. **Test thoroughly**: Include attack and defense test cases
3. **Make configurable**: Allow users to enable/disable
4. **Update whitelist/blacklist**: Add new entries if needed

### Configuration Options

When adding configuration options:

1. Add to `SecurityConfig` dataclass
2. Update `__post_init__` if needed
3. Document in README
4. Add example usage
5. Test with different configurations

## Documentation

### Update README

When adding features:

1. Update feature list
2. Add usage examples
3. Update API documentation
4. Add configuration details

### Update Chinese Documentation

Also update `docs/README_CN.md` with Chinese translations.

### Code Comments

Add clear comments:

```python
def check_gas(self) -> None:
    """Check and consume Gas - high-frequency function
    
    This function is called at every loop iteration and function call
    to prevent CPU DoS attacks. When Gas quota is exhausted, it raises
    GasLimitExceeded exception.
    
    Raises:
        GasLimitExceeded: When Gas quota is exhausted
    """
    if self._current_gas <= 0:
        raise GasLimitExceeded(...)
```

## Release Process

### 1. Update Version

Update version in:
- `setup.py`
- `pyproject.toml`
- `src/secure_sandbox/__init__.py`

### 2. Update Changelog

Create `CHANGELOG.md`:

```markdown
## [1.1.0] - 2025-06-05
### Added
- Custom module whitelist support
- Memory monitoring feature

### Changed
- Improved Gas mechanism performance

### Fixed
- Bug in attribute interception
```

### 3. Build Package

```bash
python -m build
```

### 4. Test Installation

```bash
pip install dist/secure_sandbox-1.1.0.tar.gz
pytest tests/
```

### 5. Publish to PyPI

```bash
twine upload dist/*
```

## Questions?

- Open an Issue for bugs or feature requests
- Email: security@example.com

Thank you for contributing! 🎉