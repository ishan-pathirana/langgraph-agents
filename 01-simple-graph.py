import langgraph
import random

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

"""
This is simple graph in langgraph.
There are 3 nodes
After node 1, There is a function to decide mood
Based on the decision, node 2 or 3 will be executed
"""

# Create the agent state

class State(TypedDict):
    graph_state: str

# Define nodes

def node_1(state: State) -> State:
    return {"graph_state": state["graph_state"] + " I am"}

def node_2(state: State) -> State:
    return {"graph_state": state["graph_state"] + " happy!"}

def node_3(state: State) -> State:
    return {"graph_state": state["graph_state"] + " sad!"}


# Define function for conditional edges

def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    
    if random.random() < 0.5:
        return "node_2"

    return "node_3"

# Define graph

builder = StateGraph(State)

# Add nodes

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Add edges

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile graph

graph = builder.compile()

# Invoke graph

print(graph.invoke({"graph_state": "Hi, This is Ishan."}))
