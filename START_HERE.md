# 🚀 Quick Start - Arr Suite MCP Server

## ✅ Configuration Complete!

Your MCP server is **ready to use** in Claude Code and VS Code (Roo/Cline).

## 🎯 Immediate Actions

### 1. Test in Claude Code (Right Now!)

Open Claude Code in either project directory and try:

```
List all configured arr services
```

You should see: Sonarr, Radarr, Prowlarr, Overseerr, and Plex (pending token)

### 2. Try Natural Language

```
Search Radarr for The Matrix
```

```
Show all my TV series in Sonarr
```

```
What indexers are configured in Prowlarr?
```

### 3. Get Plex Token (Optional but Recommended)

**Quick Method:**
1. Go to https://app.plex.tv
2. Play any media
3. Click "..." → "Get Info" → "View XML"
4. Copy the `X-Plex-Token` from URL

**Add to `.env`:**
```bash
PLEX_TOKEN=your_actual_token
```

Then restart Claude Code or reload the MCP server.

## 📝 What's Configured

### ✅ Services Ready
- **Sonarr** @ localhost:8989
- **Radarr** @ localhost:7878
- **Prowlarr** @ localhost:9696
- **Overseerr** @ localhost:5055
- **Plex** @ localhost:32400 (needs token)

### ✅ MCP Configurations
- `/opt/docker-media-server/.claude/mcp_config.json` (docker-media-server)
- `/opt/docker-media-server/arr-suite-mcp-server/.claude/mcp_config.json` (this project)

## 🎮 Example Commands

### Media Management
```
Add Breaking Bad to Sonarr
```

```
Search for movies from 2023 in Radarr
```

```
Request Avatar 2 through Overseerr
```

### System Operations
```
Show download queue status
```

```
Get system status for all services
```

```
List all quality profiles in Radarr
```

### Plex (after adding token)
```
What's recently added to Plex?
```

```
Search Plex for Breaking Bad
```

```
Show what's currently playing
```

## 📚 Documentation

- **Full Setup Guide**: [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md)
- **Plex Integration**: [PLEX_INTEGRATION.md](PLEX_INTEGRATION.md)
- **Usage Examples**: [EXAMPLES.md](EXAMPLES.md)
- **README**: [README.md](README.md)

## 🔧 For VS Code / Roo / Cline Users

The `.claude/mcp_config.json` file is already created and will be auto-detected.

If not working, see [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md) for manual configuration.

## ✨ Smart Features

### Natural Language Understanding
Just describe what you want:
- "Add this movie" → Routes to Radarr
- "Download subtitles" → Routes to Bazarr
- "Search indexers" → Routes to Prowlarr
- "Request media" → Routes to Overseerr

### Intelligent Routing
The system automatically detects:
- Service (Sonarr, Radarr, etc.)
- Operation (search, add, delete, etc.)
- Context (titles, years, quality, etc.)

## 🎯 First Steps Checklist

- [ ] Test: `List all configured services`
- [ ] Try: `Search Radarr for a movie`
- [ ] Get Plex token and add to `.env`
- [ ] Test: `What's new on Plex?`
- [ ] Explore: Use `arr_explain_intent` to understand queries

## 🐛 Issues?

See [CLAUDE_CODE_SETUP.md](CLAUDE_CODE_SETUP.md) → Troubleshooting section

---

**Everything is configured and ready to go!** 🎉

Start using it immediately in Claude Code by asking: `"List all configured arr services"`
