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

# Initialize models
model = init_chat_model(model="anthropic:claude-sonnet-4-20250514")
model_with_tools = model.bind_tools(tools)
summarization_model = init_chat_model(model="openai:gpt-4.1-mini")
compress_model = init_chat_model(model="openai:gpt-4.1", max_tokens=32000)

# Create Nodes for the langgraph

def DecisionNode(state: ResearcherState):
    """Based on current state and decide on next actions.
    The model analyzes the current conversation state and decides whether to:
    1. Call search tools to gather more information
    2. Provide a final answer based on gathered information
    Returns updated state with the model's response.
    """
    return {
        "researcher_messages": [
            model_with_tools.invoke(
                [SystemMessage(content=research_agent_prompt)] + state["researcher_messages"]
            )
        ]
    }

def RouterNode(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """
    Determines the next step in the workflow based on the current State
    Determines whether the agent should continue the research loop or provide
    a final answer based on whether the LLM made tool calls.
    Returns:
        "tool_node": Continue to tool execution
        "compress_research": Stop and compress research
    """
    messages = state["researcher_messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, continue to tool execution
    if last_message.tool_calls:
        return "tool_node"
    # Otherwise, we have a final answer
    return "compress_research"




def ToolsNode(state:ResearcherState):
    """
    Executes all the tool calls based on LLMs response
    Returns the updated state with tool execution result
    """
    tool_calls = state["researcher_messages"][-1].tool_calls

    # Execute all tool calls
    observations = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observations.append(tool.invoke(tool_call["args"]))

    # Create tool message outputs
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        ) for observation, tool_call in zip(observations, tool_calls)
    ]

    return {"researcher_messages": tool_outputs}

def CompressionNode(state: ResearcherState) -> dict:
    """Compress research findings into a concise summary.

    Takes all the research messages, system prompts, Human research prompts  and tool outputs and creates
    a compressed summary suitable for the supervisor's decision-making.
    """
    system_message = compress_research_system_prompt.format(date=get_today_str())
    messages = [SystemMessage(content=system_message)] + state.get("researcher_messages", []) + [HumanMessage(content=compress_research_human_message)]
    response = compress_model.invoke(messages)

    # Extract raw notes from tool and AI messages
    raw_notes = [
        str(m.content) for m in filter_messages(
            state["researcher_messages"], 
            include_types=["tool", "ai"]
        )
    ]

    return {
        "compressed_research": str(response.content),
        "raw_notes": ["\n".join(raw_notes)]
    }

# Build the agent workflow
agent_builder = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

# Add nodes to the graph
agent_builder.add_node("llm_call", DecisionNode)
agent_builder.add_node("tool_node", ToolsNode)
agent_builder.add_node("compress_research", CompressionNode)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    DecisionNode,
    {
        "tool_node": "ToolsNode", # Continue research loop
        "compress_research": "CompressionNode", # Provide final answer
    },
)
agent_builder.add_edge("tool_node", "llm_call") # Loop back for more research
agent_builder.add_edge("compress_research", END)

# Compile the agent
researcher_agent = agent_builder.compile()