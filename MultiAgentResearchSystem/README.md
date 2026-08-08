# MultiAgentResearchSystem

A Streamlit-driven multi-agent research pipeline that uses specialized AI agents to search, scrape, write, and critique information for a user-provided topic.

## Project Overview

This repository contains:

- `app.py` - Streamlit UI for entering a research topic and displaying pipeline progress/results.
- `pipeline.py` - Orchestrates the multi-agent research flow.
- `agents.py` - Builds the search, reader, writer, and critic agents using LangChain.
- `tools.py` - Defines the web search and web scraping tools used by the agents.

## How It Works

When the user submits a topic:

1. `Search Agent` gathers recent and relevant information from the web using the Tavily search tool.
2. `Reader Agent` selects relevant URLs from the search results and scrapes the page content.
3. `Writer Chain` produces a structured research report from the gathered information.
4. `Critic Chain` evaluates the report and provides feedback.

## Requirements

Install dependencies from this directory:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in `MultiAgentResearchSystem/` with required API keys and provider settings, for example:

```env
TAVILY_API_KEY=your_tavily_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
```

## Running the App

Run the Streamlit interface from the `MultiAgentResearchSystem` directory:

```bash
streamlit run app.py
```

Then enter a research topic and press **Run Research Pipeline**.

## Notes

- The app currently uses `langchain`, `langchain-google-genai`, `langchain-groq`, and `tavily-python`.
- The `tools.py` module uses `requests` and `BeautifulSoup` to scrape page content.
- Output is displayed in the UI as a final report, critic evaluation, and raw pipeline result data.

## Project Structure

- `app.py` - Streamlit UI and state management.
- `pipeline.py` - Pipeline orchestration and execution.
- `agents.py` - Agent definitions and prompt templates.
- `tools.py` - Web search and scraping tool implementations.
- `requirements.txt` - Python dependencies.

## Note
- UI is AI generated and code is written by me 
