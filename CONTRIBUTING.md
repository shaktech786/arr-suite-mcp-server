### Contributing to Arr Suite MCP Server

Thank you for your interest in contributing! This project aims to provide the best possible integration between AI assistants and the arr suite.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features
- 🧪 Write tests

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/arr-suite-mcp.git
cd arr-suite-mcp
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=arr_suite_mcp --cov-report=html

# Run specific test file
pytest tests/test_intent_router.py

# Run with verbose output
pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black arr_suite_mcp

# Lint with ruff
ruff check arr_suite_mcp

# Type checking with mypy
mypy arr_suite_mcp

# Run all checks
black arr_suite_mcp && ruff check arr_suite_mcp && mypy arr_suite_mcp
```

### Testing Changes

1. Add tests for your changes
2. Ensure all tests pass
3. Test manually with a real arr stack
4. Update documentation

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all public methods

### Example

```python
async def add_movie(
    self,
    tmdb_id: int,
    quality_profile_id: int,
    root_folder_path: str,
    monitored: bool = True
) -> dict[str, Any]:
    """
    Add a new movie to Radarr.

    Args:
        tmdb_id: TMDB ID of the movie
        quality_profile_id: Quality profile to use
        root_folder_path: Root folder path for the movie
        monitored: Whether to monitor the movie

    Returns:
        Added movie data

    Raises:
        ValueError: If movie not found
        ArrClientError: If API request fails
    """
    # Implementation here
    pass
```

## Project Structure

```
arr-suite-mcp/
├── arr_suite_mcp/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── server.py           # Main MCP server
│   ├── clients/            # API clients for each service
│   │   ├── base.py
│   │   ├── sonarr.py
│   │   ├── radarr.py
│   │   └── ...
│   ├── routers/            # Intent routing logic
│   │   └── intent_router.py
│   └── utils/              # Utility functions
│       └── db_manager.py
├── tests/                  # Test suite
├── docs/                   # Documentation
└── pyproject.toml         # Package configuration
```

## Adding a New Feature

### 1. Adding a New Service

To add support for a new arr service (e.g., Lidarr):

1. Create client in `arr_suite_mcp/clients/lidarr.py`:

```python
from .base import BaseArrClient

class LidarrClient(BaseArrClient):
    @property
    def service_name(self) -> str:
        return "Lidarr"

    async def get_all_artists(self) -> list[dict[str, Any]]:
        return await self.get("artist")
```

2. Add configuration in `arr_suite_mcp/config.py`:

```python
class LidarrConfig(ArrServiceConfig):
    port: int = Field(default=8686)
    model_config = SettingsConfigDict(env_prefix="LIDARR_")
```

3. Update intent router in `arr_suite_mcp/routers/intent_router.py`:

```python
SERVICE_KEYWORDS = {
    ArrService.LIDARR: ["music", "album", "artist", "lidarr"],
    # ... existing services
}
```

4. Add tests in `tests/test_lidarr.py`

5. Update documentation

### 2. Adding a New Tool

To add a new MCP tool:

1. Add tool definition in `server.py`:

```python
Tool(
    name="new_tool_name",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
)
```

2. Add handler:

```python
async def _handle_new_tool(self, arguments: dict) -> Any:
    # Implementation
    pass
```

3. Add to tool call router

4. Write tests

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_parse_movie_search(router):
    intent = router.parse_intent("Search for The Matrix")
    assert intent.service == ArrService.RADARR
    assert intent.operation == OperationType.SEARCH
```

### Integration Tests

Test interaction between components:

```python
async def test_radarr_search_integration():
    async with RadarrClient(url, key) as client:
        results = await client.lookup_movie("Inception")
        assert len(results) > 0
```

### Mock External Services

Use pytest fixtures for mocking:

```python
@pytest.fixture
def mock_radarr_response():
    return {
        "id": 1,
        "title": "The Matrix",
        "year": 1999
    }
```

## Documentation

### Docstrings

All public functions must have docstrings:

```python
def function_name(param: str) -> int:
    """
    Brief description.

    Longer description if needed.

    Args:
        param: Description of param

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised
    """
```

### README Updates

Update README.md when:
- Adding new features
- Changing configuration
- Adding new dependencies
- Modifying installation steps

### Changelog

Add entry to CHANGELOG.md:

```markdown
## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior of Y

### Fixed
- Fixed bug in Z
```

## Submitting Changes

### 1. Commit Messages

Use conventional commits:

```
feat: add Lidarr support
fix: correct intent parsing for TV shows
docs: update installation guide
test: add tests for Bazarr client
refactor: simplify router logic
```

### 2. Pull Request

1. Push your branch to your fork
2. Open a pull request with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)
   - Test results

### 3. Code Review

- Respond to feedback
- Make requested changes
- Keep PR updated with main branch

## Release Process

Maintainers will:

1. Review and merge PR
2. Update version in `pyproject.toml`
3. Update CHANGELOG.md
4. Create git tag
5. Publish to PyPI
6. Create GitHub release

## Community Guidelines

### Be Respectful

- Be welcoming to newcomers
- Respect different opinions
- Provide constructive feedback

### Ask Questions

- No question is too basic
- Use GitHub Discussions for questions
- Use Issues for bugs

### Help Others

- Answer questions
- Review pull requests
- Improve documentation

## Getting Help

- 📖 Read the documentation
- 💬 Ask in GitHub Discussions
- 🐛 Open an issue for bugs
- 📧 Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in the community

Thank you for contributing! 🎉
