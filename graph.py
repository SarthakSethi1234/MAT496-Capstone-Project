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

# for a new chat go to link parser for a continued chat go to chat node
def route_start(state: AgentState):
    if state.get("messages") and len(state["messages"]) > 0:
        return "chat_node"
    return "parse_link"


def check_parser_success(state: AgentState):
    if state.get("product_query"):
        return "success"
    return "fail"


def route_chat(state: AgentState):
    messages = state.get("messages", [])
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"

    if len(messages) > 5:
        return "summarize"

    return "end"

# Main Graph
workflow = StateGraph(AgentState)

workflow.add_node("parse_link", parse_link)
workflow.add_node("fallback_title_extractor", fallback_title_extractor)
workflow.add_node("research_subgraph", research_subgraph)
workflow.add_node("harvest_reviews", harvest_reviews)
workflow.add_node("generate_report", generate_report)
workflow.add_node("chat_node", chat_node)
workflow.add_node("summarize_conversation", summarize_conversation)

tools = [TavilySearchResults(max_results=3)]
workflow.add_node("tools", ToolNode(tools))

workflow.add_conditional_edges(
    START,
    route_start,
    {"chat_node": "chat_node", "parse_link": "parse_link"}
)

workflow.add_conditional_edges(
    "parse_link",
    check_parser_success,
    {"success": "research_subgraph", "fail": "fallback_title_extractor"}
)

workflow.add_edge("fallback_title_extractor", "research_subgraph")
workflow.add_edge("research_subgraph", "harvest_reviews")
workflow.add_edge("harvest_reviews", "generate_report")
workflow.add_edge("generate_report", "chat_node")

workflow.add_conditional_edges(
    "chat_node",
    route_chat,
    {"tools": "tools", "summarize": "summarize_conversation", "end": END}
)

workflow.add_edge("tools", "chat_node")
workflow.add_edge("summarize_conversation", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

