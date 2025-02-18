import os
from pprint import pprint
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END

# Define llm 
llm = ChatOpenAI(model="gpt-4o-mini")

# Define tool
def multiply(a: int, b: int) -> int:
    """
    Multiplies a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: multiplication result int
    """
    return a * b

# Bind tools to llm
llm_with_tools = llm.bind_tools([multiply])

# Define message state
class MessagesState(MessagesState):
    pass

# Define nodes
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("tool_calling_llm", tool_calling_llm)

# Add edges
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)

# Compile graph
graph = builder.compile()

# Invoke tools llm with generic message
messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
for message in messages["messages"]:
    message.pretty_print()
