from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Define nodes
def multiply(a: int, b: int) -> int:
    """Multiply a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: result of multiplication int
    """
    return a * b

def add(a: int, b: int) -> int:
    """Adds a and b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: result of addition int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b

    Args:
        a (int): first int
        b (int): second int

    Returns:
        float: result of division float
    """
    return a/b

# Create llm with tools
tools = [multiply, add, divide]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="You are a helpful assistant with performing arithmetic on a set of inputs")

def assistant(state: MessagesState):
    return {"messages": llm_with_tools.invoke([sys_msg] + state["messages"])}

# Graph
builder = StateGraph(MessagesState)

# Define nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)

# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

thread = {"configurable": {"thread_id": "1"}}

# for event in graph.stream(initial_input, thread, stream_mode="values"):
#     event["messages"][-1].pretty_print()

# Inspect the graph
state = graph.get_state(thread)
print(state.next)

# Stream the graph with no input to continue the graph execution
# for event in graph.stream(None, thread, stream_mode="values"):
#     event["messages"][-1].pretty_print()

# Create the user approval process
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

thread = {"configurable": {"thread_id": "2"}}

for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

user_approval = input("Do you want to call the tool? (yes/no): ")

if user_approval.lower() == "yes":

    for event in graph.stream(None, thread, stream_mode="values"):
        event["messages"][-1].pretty_print()
else:
    print("Operation cancelled by user")

