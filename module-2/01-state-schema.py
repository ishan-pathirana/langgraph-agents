import random
from langgraph.graph import StateGraph, START, END
from typing import Literal
from pydantic import BaseModel, field_validator, ValidationError

# Define nodes
def node_1(state):
    print("---Node 1---")
    return {"name": state.name + " is ... "}

def node_2(state):
    print("---Node 2---")
    return {"mood": "happy"}

def node_3(state):
    print("---Node 3---")
    return {"mood": "sad"}

def decide_mood(state) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        return "node_2"
    
    return "node_3"

# Define pydantic graph state
class PydanticState(BaseModel):
    name: str
    mood: str

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, value):
        if value not in ["happy", "sad"]:
            raise ValueError("Each mood must be either 'happy' or 'sad'")
        return value
    
# Define state
try:
    state = PydanticState(name="John Doe", mood="sad")
except ValidationError as e:
    print("Validation error:", e)

# Build graph
builder = StateGraph(PydanticState)

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
print(graph.invoke(PydanticState(name="Lance", mood="sad")))
