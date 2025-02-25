from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Define states
class OverallState(TypedDict):
    foo: int

class PrivateState(TypedDict):
    baz: int

# Define nodes
def node_1(state: OverallState) -> PrivateState:
    print("---Node 1---")
    return {"baz": state["foo"] + 1}

def node_2(state: PrivateState) -> OverallState:
    print("---Node 2---")
    return {"foo":  state["baz"] + 1}

# Build graph
builder = StateGraph(OverallState)

# Add nodes
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

# Add edges
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

# Compile graph
graph = builder.compile()

# Invoke grapph
print(graph.invoke({"foo": 1}))
print("---------------------\n")

##-------------------------------

# Define input output and overall schemas
class InputSchema(TypedDict):
    question: str

class OutputSchema(TypedDict):
    answer: str

class OverallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking_node(state: InputSchema) -> OverallState:
    return {"answer": "bye", "notes": "... his name is lance"}

def answer_node(state: OverallState) -> OutputSchema:
    return {"answer": " bye Lance"}

# Build graph
builder = StateGraph(OverallState, input=InputSchema, output=OutputSchema)

# Add nodes
builder.add_node("thinking_node", thinking_node)
builder.add_node("answer_node", answer_node)

# Add edges
builder.add_edge(START, "thinking_node")
builder.add_edge("thinking_node", "answer_node")
builder.add_edge("answer_node", END)

# Compile graph
graph = builder.compile()

# Invoke graph
print(graph.invoke({"question": "hi"}))