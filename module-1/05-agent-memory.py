from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Define llm
llm = ChatOpenAI(model='gpt-4o-mini')

# Define tools
def multiply(a: float, b: float) -> float:
    """
    Multiply two float numbers and 
    return the float result

    Args:
        a (float): first float
        b (float): second float

    Returns:
        float: result float
    """
    return a * b

def add(a: float, b: float) -> float:
    """
    add two float numbers and 
    return the float result

    Args:
        a (float): first float
        b (float): second float

    Returns:
        float: result float
    """
    return a + b

def divide(a: float, b: float) -> float:
    """
    devide two float numbers and 
    return result float

    Args:
        a (float): dividend float
        b (float): divisor float

    Returns:
        float: result float
    """
    return a / b

# Bind tools to llm
tools = [multiply, add, divide]
llm_with_tools = llm.bind_tools(tools)

# Define system message
sys_message = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs. ")

# Define tool node
def assistant(state: MessagesState):
    return {"messages": llm_with_tools.invoke([sys_message] + state["messages"])}

# Build graph
builder = StateGraph(MessagesState)

# Add node
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Compile graph with memory
memory = MemorySaver()
react_graph_with_memory = builder.compile(checkpointer=memory)

# Specify a thread
config = {"configurable": {"thread_id": "1"}}

# Specify an input
messages = [HumanMessage(content="Add 4 and 3.5.")]

# Run
messages = react_graph_with_memory.invoke({"messages": messages}, config=config)
for message in messages["messages"]:
    message.pretty_print()


messages = [HumanMessage(content="Multiply that by 2.")]
messages = react_graph_with_memory.invoke({"messages": messages}, config=config)
for message in messages["messages"]:
    message.pretty_print()