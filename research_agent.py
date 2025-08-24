"""
This module is the Agent implementation for the Research.
In this the LLM will be used as a Decision maker if the user
query needs further tool calls.
There will be function to do tool calls and get results for the user query
There will be a function to decide the Route based on the decision of the LLM
There will be another function to Compress the results from the tools into a response for the user query.
"""

from pydantic import BaseModel, Field
from typing_extensions import Literal

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages
from langchain.chat_models import init_chat_model

from StateObjects import ResearcherState, ResearcherOutputState
from toolUtils import tavily_search, get_today_str, think_tool
from research_prompts import research_agent_prompt, compress_research_system_prompt, compress_research_human_message


tools = [tavily_search, think_tool]
tools_by_name = {tool.name: tool for tool in tools}

