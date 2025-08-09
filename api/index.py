from mcp.server.fastmcp import FastMCP
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv  # <-- for .env support
load_dotenv()

# MCP server
app = FastMCP("LocalBusinessFinder")

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MCP_BEARER_TOKEN=os.getenv("MCP_BEARER_TOKEN")

 
genai.configure(api_key=GEMINI_API_KEY)

TAVILY_API_URL = "https://api.tavily.com/search"

@app.tool()
def validate(token: str):
    """
    Validate the Bearer token and return the user's phone number without '+'.
    """
    expected_token = os.getenv("MCP_BEARER_TOKEN")

    if token != expected_token:
        raise ValueError("Invalid token")

    # Replace with dynamic lookup if needed
    return {"phone": "919876543210"}  # Example: India number without '+'

@app.tool()
def find_local_business(query: str):
    """
    Finds top 3 local businesses using Tavily and formats via Gemini.
    """
    # Step 1: Search Tavily
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 10
    }
    response = requests.post(TAVILY_API_URL, json=payload)
    print(response)
    data = response.json()

    snippets = []
    for result in data.get("results", []):
        title = result.get("title", "No title")
        url = result.get("url", "")
        snippet = result.get("content", "")
        snippets.append(f"{title} - {snippet} ({url})")

    if not snippets:
        return {"error": "No results found"}

    # Step 2: Send to Gemini for formatting
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    I have search results about '{query}':
    {snippets}

    provide me the lists and their location link if have, in a structured way.
    """
    result = model.generate_content(prompt)

    return {"results": result.text}

if __name__ == "__main__":
    app.run()
