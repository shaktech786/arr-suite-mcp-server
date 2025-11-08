# Claude Code & VS Code Setup Guide

This MCP server is now configured for use with Claude Code and VS Code (Roo/Cline).

## ✅ What's Been Configured

### 1. Environment Variables (`.env`)
All your arr suite services are configured with API keys:
- ✅ Sonarr (localhost:8989)
- ✅ Radarr (localhost:7878)
- ✅ Prowlarr (localhost:9696)
- ✅ Overseerr (localhost:5055)
- ✅ Plex (localhost:32400) - **Token needed**

### 2. MCP Configuration Files Created

**For this project** (`.claude/mcp_config.json`):
- Located in `/opt/docker-media-server/arr-suite-mcp-server/.claude/`

**For docker-media-server** (`.claude/mcp_config.json`):
- Located in `/opt/docker-media-server/.claude/`

Both configurations point to the same MCP server with all your credentials.

## 🚀 Usage in Claude Code

The MCP server is automatically detected in Claude Code when you're working in either:
- `/opt/docker-media-server/arr-suite-mcp-server/` (this project)
- `/opt/docker-media-server/` (docker-media-server project)

### Try These Commands

```
List all configured arr services
```

```
Search Radarr for The Matrix
```

```
Show my Sonarr TV series
```

```
Get recently added Plex media
```

```
List all Prowlarr indexers
```

## 🔧 For VS Code / Roo / Cline

### Option 1: Use MCP Extension (Recommended)

1. Install MCP extension in VS Code Insiders
2. The `.claude/mcp_config.json` will be auto-detected
3. Reload window
4. MCP server will be available

### Option 2: Manual Roo/Cline Configuration

Add to your Roo/Cline settings:

```json
{
  "mcp": {
    "servers": {
      "arr-suite": {
        "command": "python3",
        "args": ["-m", "arr_suite_mcp.server"],
        "cwd": "/opt/docker-media-server/arr-suite-mcp-server",
        "env": {
          "PYTHONPATH": "/path/to/arr-suite-mcp-server",
          "SONARR_HOST": "localhost",
          "SONARR_PORT": "8989",
          "SONARR_API_KEY": "your_sonarr_api_key_here",
          "RADARR_HOST": "localhost",
          "RADARR_PORT": "7878",
          "RADARR_API_KEY": "your_radarr_api_key_here",
          "PROWLARR_HOST": "localhost",
          "PROWLARR_PORT": "9696",
          "PROWLARR_API_KEY": "your_prowlarr_api_key_here",
          "OVERSEERR_HOST": "localhost",
          "OVERSEERR_PORT": "5055",
          "OVERSEERR_API_KEY": "your_overseerr_api_key_here",
          "PLEX_HOST": "localhost",
          "PLEX_PORT": "32400",
          "PLEX_TOKEN": "your_plex_token_here"
        }
      }
    }
  }
}
```

## 📝 Getting Plex Token (Optional but Recommended)

You currently don't have a Plex token configured. To enable Plex features:

### Method 1: From Plex Web App
1. Open https://app.plex.tv
2. Browse to any media item
3. Click "..." → "Get Info" → "View XML"
4. Look for `X-Plex-Token` in the URL
5. Copy the token value

### Method 2: Using curl
```bash
curl -X POST 'https://plex.tv/users/sign_in.json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'user[login]=YOUR_EMAIL&user[password]=YOUR_PASSWORD'
```

### Add Token
Once you have the token, add it to:
1. `/opt/docker-media-server/arr-suite-mcp-server/.env`:
   ```bash
   PLEX_TOKEN=your_actual_token_here
   ```

2. Both `.claude/mcp_config.json` files:
   ```json
   "PLEX_TOKEN": "your_actual_token_here"
   ```

## 🧪 Testing the MCP Server

### Test in Claude Code
```
Explain what "Add Breaking Bad to Sonarr" would do
```

Should show you how it would route the request.

### Test Direct Tool Access
```
Use the sonarr_get_series tool to list all my TV shows
```

### Test Natural Language
```
Search Radarr for movies released in 2023
```

## 📊 Available MCP Tools

### Intelligent Router
- `arr_execute` - Execute any operation using natural language
- `arr_explain_intent` - See how your query will be interpreted
- `arr_list_services` - Show which services are configured
- `arr_get_system_status` - Check health of all services

### Service-Specific Tools

**Sonarr** (3 tools + more):
- `sonarr_search_series`
- `sonarr_add_series`
- `sonarr_get_series`

**Radarr** (3 tools + more):
- `radarr_search_movie`
- `radarr_add_movie`
- `radarr_get_movies`

**Prowlarr** (3 tools):
- `prowlarr_search`
- `prowlarr_get_indexers`
- `prowlarr_sync_apps`

**Bazarr** (2 tools):
- `bazarr_search_subtitles`
- `bazarr_download_subtitle`

**Overseerr** (3 tools):
- `overseerr_search`
- `overseerr_request`
- `overseerr_get_requests`

**Plex** (7 tools):
- `plex_get_libraries`
- `plex_search`
- `plex_get_recently_added`
- `plex_get_on_deck`
- `plex_get_sessions`
- `plex_scan_library`
- `plex_mark_watched`

## 🔍 Troubleshooting

### MCP Server Not Showing in Claude Code

1. Check if `.claude/mcp_config.json` exists:
   ```bash
   ls -la /opt/docker-media-server/.claude/
   ls -la /opt/docker-media-server/arr-suite-mcp-server/.claude/
   ```

2. Verify Python can find the module:
   ```bash
   cd /opt/docker-media-server/arr-suite-mcp-server
   PYTHONPATH=/opt/docker-media-server/arr-suite-mcp-server python3 -m arr_suite_mcp.server --help
   ```

3. Check MCP server logs in Claude Code output panel

### Services Not Connecting

Verify services are reachable:
```bash
curl -H "X-Api-Key: YOUR_SONARR_API_KEY" \
  http://localhost:8989/api/v3/system/status
```

### Python Module Not Found

Make sure PYTHONPATH is set in the MCP config:
```json
"env": {
  "PYTHONPATH": "/opt/docker-media-server/arr-suite-mcp-server"
}
```

## 🎯 Next Steps

1. ✅ MCP configs are created
2. ⏳ Get Plex token and add to `.env`
3. ⏳ Test in Claude Code: "List all configured services"
4. ⏳ Try natural language queries
5. ⏳ Explore all the available tools

## 📁 File Locations

- **MCP Config (this project)**: `/opt/docker-media-server/arr-suite-mcp-server/.claude/mcp_config.json`
- **MCP Config (docker-media-server)**: `/opt/docker-media-server/.claude/mcp_config.json`
- **Environment Variables**: `/opt/docker-media-server/arr-suite-mcp-server/.env`
- **Server Code**: `/opt/docker-media-server/arr-suite-mcp-server/arr_suite_mcp/`

## 💡 Pro Tips

1. **Use Natural Language**: The router is smart - just describe what you want
2. **Check Intent First**: Use `arr_explain_intent` to see how it will be interpreted
3. **Direct Tools**: For precise control, use service-specific tools
4. **System Status**: Regularly check `arr_get_system_status`
5. **Database Backup**: The server includes database management utilities

---

**Ready to use in both Claude Code and VS Code (Roo/Cline)!** 🚀
