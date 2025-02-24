from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage, RemoveMessage
from langgraph.graph.message import MessagesState, add_messages
from typing import TypedDict, Annotated

# Define custom reducer
def reduce_list(left: list | None, right: list | None) -> list:
    """Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
            If an input is None, it's treated as an empty list.
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right

# Define custom reducer state
class CustomReducerState(TypedDict):
    foo: Annotated[list[int], reduce_list]

# Define node
def node_1(state):
    print("---Node 1---")
    return {"foo": [2]}

# Build graph
builder = StateGraph(CustomReducerState)

# Add node
builder.add_node("node_1", node_1)

# Add edges (logic)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Compile graph
graph = builder.compile()

# Invoke graph
print(graph.invoke({"foo": None}))
print("-------------------------------")

##-------------------##

# Define custom message state
class CustomMessageState(MessagesState):
    added_key_1: str
    added_key_2: str

# Initial state
initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
                    HumanMessage(content="I'm looking for information on marine biology.", name="Lance")]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interseted in?", name="Model")

# Add messages
print("\n---ADDING MESSAGES--")
print(add_messages(initial_messages, new_message))

# Initial state
initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model", id="1"),
                    HumanMessage(content="I'm looking for information on marine biology.", name="Lance", id="2")]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interseted in?", name="Model", id="2")

# Re write messages
print("\n---REWRITING MESSAGES--")
print(add_messages(initial_messages, new_message))

# Message list
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Lance", id="2"))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"))

# Isolate messages to delete
delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
print(delete_messages)

# Deleting messages
print("\n---DELETING MESSAGES--")
print(add_messages(messages, delete_messages))