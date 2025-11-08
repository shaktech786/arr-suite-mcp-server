# MCP Registry Submission

This document contains information for submitting this package to the official MCP registry.

## Package Information

**Name:** arr-suite-mcp

**Description:** MCP Server for Plex + the *arr suite of media server tools (Sonarr, Radarr, Prowlarr, Bazarr, Overseerr).

**Category:** Media & Entertainment

**Tags:** media, automation, sonarr, radarr, prowlarr, bazarr, overseerr, tv, movies, subtitles, plex, arr

## Installation

### Via pip (Recommended)
```bash
pip install arr-suite-mcp
```

### Via source
```bash
git clone https://github.com/shaktech786/arr-suite-mcp-server.git
cd arr-suite-mcp-server
pip install -e .
```

## Configuration

The server requires environment variables for each arr service you want to use:

```bash
# Minimum configuration for Sonarr
SONARR_HOST=localhost
SONARR_PORT=8989
SONARR_API_KEY=your_api_key

# Similar for other services: RADARR_, PROWLARR_, BAZARR_, OVERSEERR_
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "arr-suite": {
      "command": "arr-suite-mcp",
      "env": {
        "SONARR_HOST": "192.168.1.100",
        "SONARR_PORT": "8989",
        "SONARR_API_KEY": "your_sonarr_api_key",
        "RADARR_HOST": "192.168.1.100",
        "RADARR_PORT": "7878",
        "RADARR_API_KEY": "your_radarr_api_key"
      }
    }
  }
}
```

## Features

### Intelligent Natural Language Processing
- Automatically routes requests to appropriate service
- Understands context (years, quality, seasons, etc.)
- Supports conversational queries

### Comprehensive API Coverage
- **Sonarr**: Full TV series management (20+ operations)
- **Radarr**: Complete movie management (25+ operations)
- **Prowlarr**: Indexer management and search (15+ operations)
- **Bazarr**: Subtitle management (12+ operations)
- **Overseerr**: Request and discovery management (15+ operations)

### Database Management
- Backup and restore capabilities
- Direct SQL query execution
- Database optimization tools

### Production Ready
- Type-safe with Pydantic
- Async-first architecture
- Comprehensive error handling
- Full test coverage

## Example Usage

```
# Natural language queries
"Add Breaking Bad to my collection"
"Search for The Matrix in 4K"
"Download English subtitles for Dune"
"List all my indexers"
"Request Avatar 2"

# Advanced operations
"Backup all arr databases"
"Sync Prowlarr indexers to all apps"
"Show download queue status"
```

## Tools Provided

### High-Level Intelligent Tools
- `arr_execute` - Execute operations via natural language
- `arr_explain_intent` - Understand query interpretation
- `arr_list_services` - Show configured services
- `arr_get_system_status` - Health check all services

### Service-Specific Tools
- 60+ specialized tools across all services
- Direct API access for precise control
- Batch operations support

## Requirements

- Python 3.10+
- At least one arr service (Sonarr, Radarr, Prowlarr, Bazarr, or Overseerr)
- API keys for configured services

## Documentation

- README.md - Comprehensive overview and quick start
- INSTALL.md - Detailed installation guide
- EXAMPLES.md - Usage examples and workflows
- API documentation inline with type hints

## Support

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and community support
- Comprehensive error messages and logging

## License

MIT License

## Maintainers

See CONTRIBUTORS.md

## Links

- Repository: https://github.com/shaktech786/arr-suite-mcp-server
- PyPI: https://pypi.org/project/arr-suite-mcp
- Documentation: https://github.com/shaktech786/arr-suite-mcp-server#readme
- Issues: https://github.com/shaktech786/arr-suite-mcp-server/issues

## Quality Metrics

- ✅ Full type hints
- ✅ Comprehensive test suite
- ✅ Code formatted with Black
- ✅ Linted with Ruff
- ✅ Type checked with Mypy
- ✅ Async-first design
- ✅ Production ready

## Why This MCP Server?

1. **Unified Interface**: Single integration for entire media stack
2. **Natural Language**: Talk to your media server naturally
3. **Intelligent Routing**: Automatically determines correct service
4. **Complete Coverage**: All major arr services supported
5. **Battle Tested**: Built on proven arr APIs
6. **Easy Setup**: Simple environment variable configuration
7. **Extensible**: Easy to add new services and features

## Changelog

See CHANGELOG.md for version history.

## Screenshots

(Add screenshots of Claude Desktop using the MCP server)

## Video Demo

(Link to demo video showing natural language interactions)
