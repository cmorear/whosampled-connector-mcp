# Claude Desktop App Configuration

This guide shows how to configure the whosampled-connector MCP server for use with Claude Desktop app.

## Configuration File Location

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## Configuration Methods

### Method 1: Using uvx (Recommended for Quick Setup)

**Prerequisites:**
1. Install uvx: https://docs.astral.sh/uv/
2. Install Playwright browsers once: `uvx playwright install chromium`

**Configuration:**

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "whosampled-mcp": {
      "command": "python",
      "args": [
        "-m",
        "whosampled_connector"
      ],
      // CRITICAL: Set this path to your exact directory!
      "cwd": "C:\\Users\\Moorman\\Desktop\\whosampled-connector-mcp" 
    }
  }
}
```

### Method 2: Using Local Installation (Recommended for Development)

**Prerequisites:**
1. Clone the repository
2. Install dependencies: `uv sync`
3. Install Playwright browsers: `uv run playwright install chromium`

**Configuration (Windows):**

```json
{
  "mcpServers": {
    "whosampled-mcp": {
      "command": "C:\\path\\to\\whosampled-connector-mcp\\.venv\\Scripts\\whosampled-connector.exe"
    }
  }
}
```

**Configuration (macOS/Linux):**

```json
{
  "mcpServers": {
    "whosampled-mcp": {
      "command": "/path/to/whosampled-connector-mcp/.venv/bin/whosampled-connector"
    }
  }
}
```

### Method 3: Using Python Directly

**Prerequisites:**
1. Clone and install the package
2. Install Playwright browsers

**Configuration:**

```json
{
  "mcpServers": {
    "whosampled-mcp": {
      "command": "python",
      "args": [
        "-m",
        "whosampled_connector"
      ],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\whosampled-connector-mcp\\src"
      }
    }
  }
}
```

## Troubleshooting

### Error: "Unknown option: 'from'"

This means the `uvx` command and its arguments are not being parsed correctly. Make sure you're using Method 1 format with `args` as a JSON array.

**Wrong:**
```json
{
  "command": "uvx --from git+https://... whosampled-connector"
}
```

**Correct:**
```json
{
  "command": "uvx",
  "args": ["--from", "git+https://...", "whosampled-connector"]
}
```

### Error: "Playwright browsers not found"

Run this command once before using the server:
```bash
uvx playwright install chromium
```

### Server disconnects immediately

Check the Claude Desktop app logs:
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.config/Claude/logs/`

### Testing the configuration

After adding the configuration:
1. Restart Claude Desktop app completely
2. Open a new conversation
3. Look for the MCP server icon or tools
4. Try using the whosampled-connector tools

## Example Usage in Claude

Once configured, you can ask Claude:
- "Search for samples used in Daft Punk's Harder Better Faster Stronger"
- "What tracks sampled One More Time by Daft Punk?"
- "Get sampling information for [artist] - [track]"
