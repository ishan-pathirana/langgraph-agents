from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.graph.message import MessagesState
from langgraph.graph import StateGraph, START, END

# Define llm
llm = ChatOpenAI(model="gpt-4o-mini")

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

# Bind tools to LLM
tools = [multiply, add, divide]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# Define system message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs. ")

# Define nodes
def assistant(state: MessagesState) -> dict:
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# compile graph
react_graph = builder.compile()

# Invoke agent with generic message
# messages = [HumanMessage(content="Hello")]
# messages = react_graph.invoke({"messages": messages})
# for message in messages["messages"]:
#     message.pretty_print()

# Invoke agent with tool call
messages = [HumanMessage(content="Add 4 and 3.5. Multiply the output by 2. Divide the output by 5")]
messages =  react_graph.invoke({"messages": messages})
for message in messages["messages"]:
    message.pretty_print()