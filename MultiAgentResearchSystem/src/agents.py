from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools import web_search , scrape_tool 
from dotenv import load_dotenv

load_dotenv()

# Initializing the LLMs
llm_groq = ChatGroq(model = "openai/gpt-oss-120b")
llm_gemini = ChatGoogleGenerativeAI(model='gemini-3.5-flash')

# Agent-1: Search the web using the web search tool
def build_search_agent():
    return create_agent(
        model=llm_groq,
        tools=[web_search]
    )

# Agent-2: Scrape the web content using the web scraping tool
def build_reader_agent():
    return create_agent(
        model=llm_gemini,
        tools=[scrape_tool]
    )


# Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm_groq | StrOutputParser()

# Critic chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm_gemini | StrOutputParser()
