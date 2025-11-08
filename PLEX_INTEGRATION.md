# Plex Integration Guide

Complete guide for using Plex with the Arr Suite MCP Server.

## Overview

The Plex integration provides comprehensive control over your Plex Media Server through natural language and direct API calls. Manage libraries, playback, search media, and monitor server activity all through the MCP interface.

## Configuration

### 1. Get Your Plex Token

You need a Plex authentication token to connect. Here are several methods:

#### Method 1: From Plex Web App (Easiest)
1. Sign in to Plex Web App (app.plex.tv)
2. Browse to any media item
3. Click the "..." menu → "Get Info"
4. Click "View XML"
5. Look for `X-Plex-Token` in the URL

#### Method 2: Using curl
```bash
curl -X POST 'https://plex.tv/users/sign_in.json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'user[login]=YOUR_EMAIL&user[password]=YOUR_PASSWORD'
```

The response will include your token.

#### Method 3: From Account Settings
1. Visit https://www.plex.tv/claim/
2. Copy the claim token (note: this expires in 4 minutes)

### 2. Configure Environment

Add to your `.env` file:

```bash
PLEX_HOST=localhost          # or your Plex server IP
PLEX_PORT=32400             # default Plex port
PLEX_TOKEN=your_token_here
PLEX_SSL=false              # true if using HTTPS
```

### 3. Verify Connection

Test your configuration:

```
Get Plex system status
```

Should return your server information.

## Features

### Library Management

#### List All Libraries
```
Show my Plex libraries
List all Plex libraries
```

Returns all your library sections (Movies, TV Shows, Music, etc.)

#### Get Library Contents
```python
# Using specific tool
plex_get_library_items(section_id=1)
```

#### Scan Library
```
Scan my Movies library
Refresh Plex TV Shows library
```

Triggers Plex to scan for new content.

#### Empty Trash
```python
# Direct API call
await plex.empty_library_trash(section_id=1)
```

### Search and Discovery

#### Search Media
```
Search Plex for Breaking Bad
Find The Matrix in Plex
Search for Inception
```

Searches across all your libraries.

#### Recently Added
```
What's new on Plex?
Show recently added to Plex
Get recently added media
```

Returns your most recently added content.

#### On Deck
```
Show my On Deck
What should I watch next?
Get On Deck items
```

Returns media you're currently watching (in progress).

### Playback and Sessions

#### Active Sessions
```
What's playing on Plex?
Show current Plex sessions
Who's watching Plex?
```

Shows all active playback sessions.

#### Terminate Session
```python
# Requires session ID
await plex.terminate_session(
    session_id="abc123",
    reason="Server maintenance"
)
```

#### Watch Status
```
Mark The Matrix as watched
Mark Breaking Bad S01E01 as watched
```

Updates watch status for items.

### Collections and Playlists

#### Get Collections
```python
collections = await plex.get_collections(section_id=1)
```

#### Create Collection
```python
await plex.create_collection(
    section_id=1,
    title="Marvel Movies",
    items=["123", "456", "789"]
)
```

#### Get Playlists
```
Show my Plex playlists
```

#### Create Playlist
```python
await plex.create_playlist(
    title="Action Movies",
    items=["movie1_key", "movie2_key"]
)
```

### Server Management

#### Server Status
```
Get Plex server status
Check Plex health
```

#### Server Statistics
```python
stats = await plex.get_server_stats()
bandwidth = await plex.get_bandwidth_stats(timespan=6)
```

#### Optimize Database
```python
await plex.optimize_database()
```

#### Clean Bundles
```python
await plex.clean_bundles()
```

### Transcoding

#### Active Transcodes
```python
sessions = await plex.get_transcode_sessions()
```

#### Kill Transcode
```python
await plex.kill_transcode_session(session_key="abc123")
```

### Butler Tasks

Plex Butler handles scheduled maintenance tasks.

#### List Tasks
```python
tasks = await plex.get_butler_tasks()
```

#### Run Task
```python
# Backup database
await plex.start_butler_task("BackupDatabase")

# Optimize database
await plex.start_butler_task("OptimizeDatabase")

# Clean old bundles
await plex.start_butler_task("CleanOldBundles")
```

## Natural Language Examples

The MCP server intelligently routes Plex queries:

### Simple Queries
- "Search Plex for movies"
- "Show my libraries"
- "What's new on Plex?"

### Contextual Queries
- "Is The Matrix on my Plex server?"
- "Show what's currently playing"
- "Mark episode 5 as watched"

### Management Queries
- "Scan my Movies library for new content"
- "Show Plex server statistics"
- "Optimize Plex database"

## MCP Tools

### Available Plex Tools

1. **plex_get_libraries** - List all libraries
2. **plex_search** - Search for media
3. **plex_get_recently_added** - Recently added content
4. **plex_get_on_deck** - In-progress content
5. **plex_get_sessions** - Currently playing
6. **plex_scan_library** - Scan for new content
7. **plex_mark_watched** - Update watch status

### Tool Usage Examples

```python
# Search
result = await mcp.call_tool("plex_search", {"query": "Matrix"})

# Get libraries
libraries = await mcp.call_tool("plex_get_libraries", {})

# Scan library (section_id from get_libraries)
await mcp.call_tool("plex_scan_library", {"section_id": 1})

# Mark watched
await mcp.call_tool("plex_mark_watched", {"rating_key": "12345"})
```

## Integration with Arr Suite

Plex works seamlessly with other arr services:

### Complete Workflow
1. **Request** media through Overseerr
2. **Download** via Sonarr/Radarr
3. **Auto-add** to Plex library
4. **Search** and **play** in Plex

### Example: Add and Watch Movie
```
1. "Request The Matrix"           (Overseerr)
2. Wait for download...           (Radarr + qBittorrent)
3. "Scan Movies library"          (Plex)
4. "Search Plex for The Matrix"   (Plex)
5. Play in Plex app
```

### Monitoring Workflow
```
1. "Show Plex sessions"           (Who's watching)
2. "Get recently added"           (New content)
3. "Show On Deck"                 (Resume watching)
```

## Advanced Usage

### Custom Queries

The intent router understands Plex-specific keywords:

- **library, libraries** → Get libraries
- **playing, sessions** → Active playback
- **watched** → Watch status
- **on deck** → In-progress
- **recently added** → New content
- **scan, refresh** → Update library

### Direct API Access

For advanced operations, use the Plex client directly:

```python
from arr_suite_mcp.clients import PlexClient

async with PlexClient(base_url, token) as plex:
    # Get detailed metadata
    item = await plex.get_metadata("12345")

    # Update metadata
    await plex.update_metadata(
        "12345",
        title="New Title",
        summary="New description"
    )

    # Advanced search
    results = await plex.search(
        query="action",
        section_id=1,
        limit=50
    )
```

## Troubleshooting

### Connection Issues

**Problem**: Can't connect to Plex server

**Solutions**:
1. Verify Plex is running
2. Check firewall allows port 32400
3. Ensure correct IP/hostname
4. Verify token is valid

### Token Issues

**Problem**: Authentication failed

**Solutions**:
1. Generate new token
2. Check token hasn't expired
3. Verify you're using X-Plex-Token, not claim token

### Library Not Updating

**Problem**: New media not appearing

**Solutions**:
```
# Force scan
"Scan my Movies library"

# Or with force flag
await plex.scan_library(section_id=1)
```

### Slow Performance

**Problem**: Plex responding slowly

**Solutions**:
```python
# Optimize database
await plex.optimize_database()

# Clean old bundles
await plex.clean_bundles()

# Check active transcodes
sessions = await plex.get_transcode_sessions()
```

## Security Best Practices

1. **Token Security**
   - Never commit tokens to git
   - Use environment variables
   - Rotate tokens periodically

2. **Network Security**
   - Use SSL when possible (PLEX_SSL=true)
   - Limit network access
   - Use Plex's built-in authentication

3. **Access Control**
   - Use Plex managed users
   - Enable PIN protection
   - Review sharing settings

## Performance Tips

1. **Enable Hardware Transcoding**
   - Reduces CPU usage
   - Faster transcoding

2. **Optimize Database Regularly**
   ```python
   await plex.optimize_database()
   ```

3. **Clean Old Bundles**
   ```python
   await plex.clean_bundles()
   ```

4. **Limit Concurrent Streams**
   - Monitor active sessions
   - Set transcode limits

## API Coverage

The Plex client provides 50+ methods covering:

- ✅ Library management
- ✅ Search and metadata
- ✅ Playback and sessions
- ✅ Collections and playlists
- ✅ Users and sharing
- ✅ Transcoding control
- ✅ Server administration
- ✅ Statistics and monitoring
- ✅ Butler tasks
- ✅ Watch status

## Resources

- [Plex API Documentation](https://www.plex.tv/api/)
- [Finding X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
- [Plex Web API](https://github.com/Arcanemagus/plex-api/wiki)
- [Official Plex Support](https://support.plex.tv/)

## Examples

See [EXAMPLES.md](EXAMPLES.md) for more Plex usage examples integrated with the full arr suite workflow.
