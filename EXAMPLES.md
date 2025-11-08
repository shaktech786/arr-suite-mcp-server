# Usage Examples

Comprehensive examples for using the Arr Suite MCP Server.

## Table of Contents

- [Basic Operations](#basic-operations)
- [TV Shows (Sonarr)](#tv-shows-sonarr)
- [Movies (Radarr)](#movies-radarr)
- [Indexers (Prowlarr)](#indexers-prowlarr)
- [Subtitles (Bazarr)](#subtitles-bazarr)
- [Requests (Overseerr)](#requests-overseerr)
- [Advanced Workflows](#advanced-workflows)
- [Database Management](#database-management)

## Basic Operations

### Understanding Intent

Before executing operations, you can see how the system will interpret your query:

```
Explain how "Add Breaking Bad to my collection" would be handled
```

Response:
```
Service: Sonarr (85% confident)
Operation: Add
Context:
  - title: Breaking Bad
  - monitored: true
  - search_on_add: true
```

### List Available Services

```
List all configured arr services
```

### Get System Status

```
Get system status for all arr services
```

## TV Shows (Sonarr)

### Adding TV Shows

Basic add:
```
Add The Mandalorian
```

Add with specific options:
```
Add Game of Thrones and monitor all seasons
```

Add without searching:
```
Add The Office but don't search for it yet
```

### Searching for Shows

```
Search for Breaking Bad
Find shows with "Star" in the title
Look up The Wire
```

### Managing Episodes

```
Get all episodes of Stranger Things
Show me episodes from season 4 of The Office
Download episode 5 of Breaking Bad season 2
```

### Monitoring

```
Monitor The Mandalorian for new episodes
Stop monitoring The Office
Monitor season 3 of Stranger Things
```

### Queue and Downloads

```
Show my download queue
Remove item 123 from the queue
Cancel download of The Office S01E01
```

### Calendar

```
Show upcoming TV episodes
What's airing this week?
Show new episodes for the next 7 days
```

## Movies (Radarr)

### Adding Movies

Basic add:
```
Add The Matrix
```

Add with quality:
```
Add Dune in 4K
Add Inception with high quality
```

Add to specific folder:
```
Add The Godfather to my movies collection
```

### Searching for Movies

```
Search for Inception
Find movies with "Star Wars" in the title
Look up The Dark Knight
```

### Collections

```
Show all my movie collections
Get all movies in The Lord of the Rings collection
Add all Marvel movies
```

### Quality Profiles

```
Show all quality profiles
Create a new 4K quality profile
Update quality settings for The Matrix
```

## Indexers (Prowlarr)

### Managing Indexers

```
List all my indexers
Show indexer statistics
Test all indexers
Add a new indexer
```

### Searching Across Indexers

```
Search for "Breaking Bad S01E01" across all indexers
Find "The Matrix 1999" on indexers
Search for 4K releases of Dune
```

### Application Sync

```
Sync indexers to Sonarr and Radarr
Refresh application connections
Update Prowlarr apps
```

### Testing and Health

```
Test indexer 5
Check health of all indexers
Show failed indexers
```

## Subtitles (Bazarr)

### Searching for Subtitles

```
Search for English subtitles for Dune
Find Spanish subtitles for Breaking Bad
Look for French subtitles for episode 5
```

### Downloading Subtitles

```
Download English subtitles for The Matrix
Get Spanish subs for Inception
Download hearing impaired subtitles for Dune
```

### Missing Subtitles

```
Show movies missing subtitles
List series without English subtitles
Find all media needing Spanish subtitles
```

### Providers

```
Show all subtitle providers
Test OpenSubtitles provider
Enable YIFY Subtitles provider
```

## Requests (Overseerr)

### Making Requests

```
Request Dune
I want to watch Avatar 2
Request Breaking Bad
```

### Managing Requests

```
Show all pending requests
List approved requests
Show my requests
```

### Approving/Declining

```
Approve request 42
Decline request 15
Approve all pending movie requests
```

### Discovery

```
Show trending movies
What TV shows are popular?
Discover new sci-fi movies
Show upcoming releases
```

### User Management

```
List all users
Show user permissions
Create a new user
```

## Advanced Workflows

### Automated Media Addition

Add a TV show and ensure subtitles:
```
1. Add The Mandalorian to Sonarr
2. Wait for download to complete
3. Search for English subtitles in Bazarr
4. Download subtitles
```

### Quality Upgrade Workflow

```
1. Search for The Matrix in Radarr
2. Check current quality
3. Search for 4K version
4. Upgrade if available
```

### Complete Setup for New Media

```
1. Request Dune in Overseerr
2. Auto-approve if configured
3. Radarr picks it up
4. Prowlarr finds best release
5. qBittorrent downloads
6. Bazarr gets subtitles
7. Plex updates library
```

### Maintenance Tasks

Daily maintenance:
```
1. Check system status of all services
2. Review download queue
3. Check for failed downloads
4. Update indexer stats
5. Backup databases
```

## Database Management

### Backing Up Databases

```python
from arr_suite_mcp.utils import ArrDatabaseManager

manager = ArrDatabaseManager()

# Backup single service
await manager.backup_database("sonarr")

# Backup all services
backups = await manager.backup_all()
print(f"Backed up: {backups}")
```

### Querying Databases

```python
# Get all series from Sonarr
series = await manager.execute_query(
    "sonarr",
    "SELECT Title, Year FROM Series"
)

# Count movies in Radarr
count = await manager.execute_query(
    "radarr",
    "SELECT COUNT(*) as total FROM Movies"
)
```

### Database Maintenance

```python
# Get database sizes
sizes = await manager.get_all_database_sizes()
print(f"Sonarr DB: {sizes['sonarr']['size_human']}")

# Vacuum database
await manager.vacuum_database("radarr")

# List tables
tables = await manager.list_tables("prowlarr")
```

## Natural Language Examples

The power of this MCP server is understanding natural language:

### Simple Queries
- "Add Breaking Bad"
- "Search for The Matrix"
- "Show my movies"

### Contextual Queries
- "Add The Office from 2005"
- "Get season 5 of Breaking Bad"
- "Download English subtitles for episode 3"

### Complex Queries
- "Search for 4K releases of Dune on all indexers"
- "Add The Mandalorian and monitor only season 1"
- "Request Avatar 2 in 4K quality"

### Configuration Queries
- "Update quality profile in Radarr"
- "Change download client settings"
- "Configure subtitle languages to English and Spanish"

### Maintenance Queries
- "Backup all databases"
- "Refresh indexers"
- "Clean up old downloads"
- "Check for failed imports"

## Error Handling

The server provides helpful error messages:

### Service Not Configured
```
> Add Breaking Bad

Error: Sonarr is not configured
Available services: radarr, overseerr

Please configure Sonarr with SONARR_HOST, SONARR_PORT, and SONARR_API_KEY
```

### Invalid API Key
```
> Search for movies

Error: Authentication failed. Check your Radarr API key.
```

### Network Issues
```
> List indexers

Error: Could not connect to Prowlarr at http://localhost:9696
Please check that Prowlarr is running and accessible.
```

## Best Practices

### 1. Start with Explanation

Before executing complex operations:
```
Explain how "Add all Marvel movies" would be handled
```

### 2. Check System Status

Before bulk operations:
```
Get system status for all arr services
```

### 3. Use Specific Commands

Instead of:
```
Do something with Breaking Bad
```

Use:
```
Add Breaking Bad to Sonarr
```

### 4. Regular Maintenance

Schedule regular tasks:
- Daily: Check queues and failed downloads
- Weekly: Backup databases
- Monthly: Review and clean up

### 5. Test Before Production

Use the explain feature to understand what will happen:
```
Explain intent: "Delete all unwatched movies from 2020"
```

## Integration with Other Tools

### With Plex

```
1. Add media via Overseerr
2. Monitor with Sonarr/Radarr
3. Download via qBittorrent
4. Subtitle with Bazarr
5. Plex auto-updates library
```

### With Custom Scripts

```python
# Custom automation script
from arr_suite_mcp import ArrSuiteMCPServer

async def auto_add_trending():
    # Get trending from Overseerr
    trending = await overseerr.get_trending_movies()

    # Add to Radarr
    for movie in trending[:10]:
        await radarr.add_movie(movie['id'])

    # Monitor downloads
    queue = await radarr.get_queue()
    return queue
```

## Troubleshooting Common Issues

### Issue: Can't find media

```
# Check if it exists
Search for "The Matrix" in Radarr

# Try alternate names
Search for "Matrix, The" in Radarr

# Search TMDB directly
Look up tmdb:603 in Radarr
```

### Issue: Download not starting

```
# Check queue
Show download queue

# Check indexers
Test all Prowlarr indexers

# Manual search
Search for "The Matrix 1999" on indexers
```

### Issue: No subtitles found

```
# Check providers
Show Bazarr subtitle providers

# Test provider
Test OpenSubtitles provider

# Manual search
Search for English subtitles for movie 123
```
