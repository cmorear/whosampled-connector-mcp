import sys
import json
import asyncio
import nest_asyncio
# Use relative import to successfully find scraper.py inside the package
from .scraper import WhoSampledScraper

# Apply patch for nested event loops (needed for synchronous loop calling async functions)
nest_asyncio.apply()

# --- MCP Tool Implementations ---

# Initialize Scraper outside of tool functions for efficiency
# Using default headless=True now that we resolved the TypeError
SCRAPER = WhoSampledScraper()

def search_track(query: str):
    """
    Tool 1: Searches for a track and returns basic information and URL.
    Input: {"query": "Daft Punk Harder Better Faster Stronger"}
    """
    if not query:
        return {"error": "Query parameter is missing."}
        
    try:
        # Run the asynchronous search function synchronously
        result = asyncio.run(SCRAPER.search_track(query))
        
        if result.get("found"):
            return {
                "title": result["title"],
                "artist": result["artist"],
                "url": result["url"],
                "message": "Track found on WhoSampled. Use get_track_samples or get_track_details_by_url for details."
            }
        else:
            return {"error": result.get("error", "No track found for the query.")}
            
    except Exception as e:
        return {"error": f"An unexpected error occurred during search: {e}"}


def get_track_samples(query: str, include_youtube: bool = False):
    """
    Tool 2: Searches for a track, then retrieves all samples, covers, and remixes.
    Input: {"query": "Kanye West Stronger", "include_youtube": true}
    """
    if not query:
        return {"error": "Query parameter is missing."}

    # 1. Search for the track first to get the URL
    search_result = search_track(query)
    if search_result.get("error"):
        return {"error": f"Search failed: {search_result['error']}"}
    
    track_url = search_result['url']
    track_title = search_result['title']

    # 2. Get detailed connections using the URL
    return get_track_details_by_url(track_url, track_title=track_title, include_youtube=include_youtube)


def get_track_details_by_url(url: str, track_title: str = "Track", include_youtube: bool = False):
    """
    Tool 3: Retrieves samples, covers, and remixes directly from a WhoSampled URL.
    Input: {"url": "https://www.whosampled.com/track/...", "include_youtube": false}
    """
    if not url or not url.startswith("http"):
        return {"error": "Invalid or missing URL parameter."}
        
    try:
        # Run the asynchronous details function synchronously
        details = asyncio.run(SCRAPER.get_track_details(url, include_youtube))
        
        if details.get("error"):
            return {"error": details["error"]}
        
        output = {
            "track": track_title,
            "url": url,
            "samples": details["samples"],
            "sampled_by": details["sampled_by"],
            "covers": details["covers"],
            "remixes": details["remixes"],
        }
        
        if include_youtube and details.get("youtube_id"):
             output["youtube"] = f"https://www.youtube.com/watch?v={details['youtube_id']}"
        elif include_youtube:
             output["youtube"] = "YouTube link not found on the WhoSampled page."

        return output
        
    except Exception as e:
        return {"error": f"An unexpected error occurred during details lookup: {e}"}


# Map tool names to their implementation functions
TOOL_MAP = {
    "search_track": search_track,
    "get_track_samples": get_track_samples,
    "get_track_details_by_url": get_track_details_by_url,
}

# --- Entry Points for Import ---

def cli():
    """
    The main loop/CLI entry point that listens for JSON requests on stdin
    and sends responses to stdout (the MCP protocol).
    """
    # Debug output should go to stderr to avoid confusing the chat client
    sys.stderr.write("WhoSampled MCP Server starting and waiting for client input...\n")
    sys.stderr.flush()

    while True:
        try:
            # Read one line (the JSON request) from stdin
            line = sys.stdin.readline()
            if not line:
                # End of file (stream closed)
                break

            request = json.loads(line)
            tool_name = request.get("tool")
            tool_args = request.get("args", {})

            if tool_name not in TOOL_MAP:
                response = {"error": f"Unknown tool: {tool_name}"}
            else:
                tool_func = TOOL_MAP[tool_name]
                # Execute the tool function with arguments
                result = tool_func(**tool_args)
                response = {"result": result}
            
            # Send the JSON response to stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            error_msg = {"error": "Invalid JSON input."}
            sys.stdout.write(json.dumps(error_msg) + "\n")
            sys.stdout.flush()
        except EOFError:
            break
        except Exception as e:
            error_msg = {"error": f"Server processing error: {e}"}
            sys.stdout.write(json.dumps(error_msg) + "\n")
            sys.stdout.flush()
            
    sys.stderr.write("WhoSampled MCP Server shutting down.\n")
    sys.stderr.flush()
    
def app():
    """
    Placeholder for the 'app' export.
    """
    return "WhoSampled MCP Server"

def main():
    """
    The standard Python entry point, aliasing to cli().
    """
    cli()