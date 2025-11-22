import os
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, ToolMessage, AIMessage
from tavily import TavilyClient
from langchain_community.tools.tavily_search import TavilySearchResults
import json

from state import AgentState, ResearchEvidence, SentimentAnalysis

def clean_json(text: str) -> str:
    """Cleans markdown code blocks from JSON string. which I dont understand"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def get_llm():
    """Returns the LLM instance."""
    api_key = os.environ.get("OPENAI_API_KEY")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)


def get_tavily():
    """Returns the Tavily client."""
    api_key = os.environ.get("TAVILY_API_KEY")
    return TavilyClient(api_key=api_key)