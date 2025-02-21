from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

# Define LLM
llm = ChatOpenAI(model='gpt-4o-mini')

# Define tool
def multiply(a: int, b: int) -> int:
    """
    Multiply a and b and returns 
    the resulting int

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: result int
    """
    return a * b

# Bind tool to llm
llm_with_tools = llm.bind_tools([multiply])

# Define messages state
class MessagesState(MessagesState):
    pass

# Define nodes
def tool_calling_llm(state: MessagesState) -> dict:
    return {"messages": llm_with_tools.invoke(state["messages"])}

# Build graph
builder =  StateGraph(MessagesState)

# Add nodes
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))

# Add edges
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", END)

# Compile graph
graph = builder.compile()

# Invoke graph with generic message
messages = [HumanMessage(content="Hello")]
messages = graph.invoke({"messages": messages})
for message in messages["messages"]:
    message.pretty_print()

# Invoke graph with tool call
messages = [HumanMessage(content="What is 2 multiplied by 2")]
messages = graph.invoke({"messages": messages})
for message in messages["messages"]:
    message.pretty_print()