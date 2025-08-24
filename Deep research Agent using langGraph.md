Deep research Agent using langGraph


PART 1
User Clarification and Brief Generation (notebooks/1_scoping.ipynb)

Purpose: Clarify research scope and transform user input into structured research briefs

Key Concepts:

User Clarification: Determines if additional context is needed from the user using structured output
Brief Generation: Transforms conversations into detailed research questions
LangGraph Commands: Using Command system for flow control and state updates
Structured Output: Pydantic schemas for reliable decision making
Implementation Highlights:

Two-step workflow: clarification → brief generation
Structured output models (ClarifyWithUser, ResearchQuestion) to prevent hallucination
Conditional routing based on clarification needs
Date-aware prompts for context-sensitive research
What You'll Learn: State management, structured output patterns, conditional routing

PART 2
Research Agent with Custom Tools (notebooks/2_research_agent.ipynb)

Purpose: Build an iterative research agent using external search tools

Key Concepts:

Agent Architecture: LLM decision node + tool execution node pattern
Sequential Tool Execution: Reliable synchronous tool execution
Search Integration: Tavily search with content summarization
Tool Execution: ReAct-style agent loop with tool calling
Implementation Highlights:

Synchronous tool execution for reliability and simplicity
Content summarization to compress search results
Iterative research loop with conditional routing
Rich prompt engineering for comprehensive research
What You'll Learn: Agent patterns, tool integration, search optimization, research workflow design

PART 3
Research Agent with MCP (notebooks/3_research_agent_mcp.ipynb)

Purpose: Integrate Model Context Protocol (MCP) servers as research tools

Key Concepts:

Model Context Protocol: Standardized protocol for AI tool access
MCP Architecture: Client-server communication via stdio/HTTP
LangChain MCP Adapters: Seamless integration of MCP servers as LangChain tools
Local vs Remote MCP: Understanding transport mechanisms
Implementation Highlights:

MultiServerMCPClient for managing MCP servers
Configuration-driven server setup (filesystem example)
Rich formatting for tool output display
Async tool execution required by MCP protocol (no nested event loops needed)
What You'll Learn: MCP integration, client-server architecture, protocol-based tool access

PART 4

Research Supervisor (notebooks/4_research_supervisor.ipynb)

Purpose: Multi-agent coordination for complex research tasks

Key Concepts:

Supervisor Pattern: Coordination agent + worker agents
Parallel Research: Concurrent research agents for independent topics using parallel tool calls
Research Delegation: Structured tools for task assignment
Context Isolation: Separate context windows for different research topics
Implementation Highlights:

Two-node supervisor pattern (supervisor + supervisor_tools)
Parallel research execution using asyncio.gather() for true concurrency
Structured tools (ConductResearch, ResearchComplete) for delegation
Enhanced prompts with parallel research instructions
Comprehensive documentation of research aggregation patterns
What You'll Learn: Multi-agent patterns, parallel processing, research coordination, async orchestration

PART 5

ull Multi-Agent Research System (notebooks/5_full_agent.ipynb)

Purpose: Complete end-to-end research system integrating all components

Key Concepts:

Three-Phase Architecture: Scope → Research → Write
System Integration: Combining scoping, multi-agent research, and report generation
State Management: Complex state flow across subgraphs
End-to-End Workflow: From user input to final research report
Implementation Highlights:

Complete workflow integration with proper state transitions
Supervisor and researcher subgraphs with output schemas
Final report generation with research synthesis
Thread-based conversation management for clarification
What You'll Learn: System architecture, subgraph composition, end-to-end workflows

Key Learning Outcomes

Structured Output: Using Pydantic schemas for reliable AI decision making
Async Orchestration: Strategic use of async patterns for parallel coordination vs synchronous simplicity
Agent Patterns: ReAct loops, supervisor patterns, multi-agent coordination
Search Integration: External APIs, MCP servers, content processing
Workflow Design: LangGraph patterns for complex multi-step processes
State Management: Complex state flows across subgraphs and nodes
Protocol Integration: MCP servers and tool ecosystems
Each notebook builds on the previous concepts, culminating in a production-ready deep research system that can handle complex, multi-faceted research queries with intelligent scoping and coordinated execution.

Scope -> Brief -> Research -> Write

Part 1 - Scope -> Generate Brief
Part 2 - Research -> Use tools and do the research with MCP too
Part 3 - Research Supervisor -> Multi agents researcher communication and handling
Part 4 - Write report

Learn :
1. Design decisions -> Why / How behind design decisions.
2. Research Agents -> Agent Design / Prompting / Using MCP
3. Multi-agent systems : Multi-agent design/ prompting
4. Evaluation - Evaluation sub components.


--------------- Scope ---------------------------

1. Conversation with User and gather the context
2. Test the system piece by piece
3. 

User clarification -> Determines additional clarification if needed.
Brief generation - Transforms tghe conversation intoa detailed research brief.

Clarification phase is to get the complete context of the user request, so AI understands the objective and context of the request correctly to give staisfactiory results.

we pass the system prompt to the chat model and request it to respond as a structured output ( Need_clarification : boolean, question: <<What is needed to clarify the request scope from the user>>, verification: << Verification message to start the research>>)

AgentInputState -> State object in LangGraph used to store state in the research workflow.
- This will hold the single message of the user rqeuest

AgentState -> Holds the internal state of the workflow which contains many fields
--------------------------------------------------------------
UserClarification

clarify_with_user -> input is agentState

pass it to the chatmodel and generate a structured output response
-> appends all the messages in the conversation.
-> if the chatmodel decides it needs clarification, then it appends the question to the messages and returns it.
-> if no clarification is needed - we mve ahead to write the researchbrief and append the verificatio question to the messages

-------------------------------------------------------------------
BriefGeneration

In write reseatch brief method, we define a structured output and invoke a chatmodel to invoke with a humanMessage which is a tranform_message_into_researchtopic_prompt using the messages and today's date.

Return the response.research_brief into the state object as well as to Supervisor messages

Evaluation

Use example of input conversations.

Write the criteria for these conversation which we want our research brief to preserve

Running in Langsmith in 3 steps:

1. Create the dataset
2. Write the evaluators
3. Run the experiment

LLM is used as Judge Evaluators
 -Better to keep a binary pass/fail judgements
 - 3-4 examples per prompt covering each scenarios.
----------------------------------------------------------------------------------------------------
Research Scope

In order to get the correct scope and generate a precise research brief for the process of research to start we need to clarify with the user the context, the intent and the scope of this research.
For this, we will leverage the structured output of the chatmodel and use classes that will store the AgentState and also create a research brief using prompts and proper structured output structure to store them 

Here the LLM does 2 things 
-> decides if the user query needs further clarification. 
-> if needs clarification - it shares the respective queries for the same.
-> if no clarification is required - prompts for validation from user to proceed with the processing of the research
-> Based on the user confirmation - it decides to start writing the brief generation.

 Research Agent
 Agent worker is the core component which will deep dive into research states

 Prompt engineering 
 Agent State
 Context engineering 

 The workflow that the agent will follow is ->
 1. It will take the research brief from the previous state
 2. Pass this to the LLM and now the LLM decides if it needs more tools to do the research and invokes those tools, else it starts processing the results for the research it does so in an iterative loop - until the agent finds the response to be satisfactory and if yes then it starts writing it back as a result.

 LLMDecisionNode -> decides if tools are ncessary of research is complete
 ToolExecutionNode -> Nodes that specicalized for calling the tools needed for the research.
 ReseearchCompressionNode -> Compresses the nodes of the all the research findings for processing
 RoutingNode - Determines the workflow based on LLMDecision node.

 Consideration:

 If not properly detailed stepwise oriented written prompt - then research agent will make unnecessary many calls to the tools.

How would you instruct your colleague

Think like an Agent:

1. Read the query carefully - what specifically the user is looking for.
2. Start with broad searches - Detailed queries first.
3. After each query - Find out if you have enough to process the research
4. Execute narrow searches -> Fill in the gaps

Concrete limits:

1. Stop when you can answer confidently
2. Budget the tool calls -> Limit the tool calls and priortize -> 2 to 3 for simple. 6 for complex query excution.
3. Limit : Stop after 5 tool calls if you cannot find the right answer.

Show your progress

1. Show the progress to user -> what information you found
2. What is missing.
3. Do I have enough information to answer the query?
4. Should I search more or provide my answer - confirm with user.
























