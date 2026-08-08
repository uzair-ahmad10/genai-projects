
from langchain.tools import tool 
from tavily import TavilyClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from rich import print
import requests
import os 

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Tool for web searching 
@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""

    results = tavily.search(query=query,max_results=5)

    output = []
    for result in results['results']:
        output.append(
            f'Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content'][:300]}\n'
        )

    return "\n------\n".join(output)

        
          
         
# Tool for scraping the text
@tool
def scrape_tool(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""

    try:
        response = requests.get(url=url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(['nav','footer', 'style','script']):
            tag.decompose()
        
        return soup.get_text(separator='', strip=True)[:3000]
    except Exception as e:
        return f"Could not find the Content: str({e})"



