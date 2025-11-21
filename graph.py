from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_community.tools.tavily_search import TavilySearchResults

from state import AgentState
from nodes import (
    parse_link, fallback_title_extractor,
    researcher_amazon, researcher_reddit, researcher_web,
    harvest_reviews, generate_report, chat_node, summarize_conversation
)

load_dotenv()

# Research Subgraph
research_builder = StateGraph(AgentState)
research_builder.add_node("researcher_amazon", researcher_amazon)
research_builder.add_node("researcher_reddit", researcher_reddit)
research_builder.add_node("researcher_web", researcher_web)

research_builder.add_edge(START, "researcher_amazon")
research_builder.add_edge(START, "researcher_reddit")
research_builder.add_edge(START, "researcher_web")

research_builder.add_edge("researcher_amazon", END)
research_builder.add_edge("researcher_reddit", END)
research_builder.add_edge("researcher_web", END)

research_subgraph = research_builder.compile()