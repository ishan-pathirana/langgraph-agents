from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver

import sqlite3

# Create llm
model = ChatOpenAI(model="gpt-4o-mini")

# Create state
class State(MessagesState):
    summary: str

# Define nodes
def call_model(state: State):
    summary = state.get("summary", "")

    if summary:
        system_message = f"Summary of the conversation earlier: {state['summary']}"

        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    response = model.invoke(messages)
    return {"messages": response}

def summarize_conversation(state: State):
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages below"
        )
    else:
        summary_message = "Create a sumamary of the conversation below"

    messages = [HumanMessage(content=summary_message)] + state["messages"]
    response = model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

# Define conditional edge logic
def should_continue(state: State):
    """Return the next node to execute."""

    messages = state["messages"]

    if len(messages) > 6:
        return "summarize_conversation"
    
    return END

# Build graph
builder = StateGraph(State)
builder.add_node("conversation", call_model)
builder.add_node(summarize_conversation)

builder.add_edge(START, "conversation")
builder.add_conditional_edges("conversation", should_continue)
builder.add_edge("summarize_conversation", END)

# Create memory
db_path = "state_db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn=conn)

# Compile graph
graph = builder.compile(checkpointer=memory)

# Create a thread
config = {"configurable": {"thread_id": "1"}}

# Start conversation
input_message = HumanMessage(content="hi! I'm Lance")
output = graph.invoke({"messages": [input_message]}, config)
for m in output["messages"][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="What's my name?")
output = graph.invoke({"messages": [input_message]}, config)
for m in output["messages"][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="i like the 49ers!")
output = graph.invoke({"messages": [input_message]}, config)
output["messages"][-1].pretty_print()

# Inspect status even after restart
graph_state = graph.get_state(config)
print("\n\n================ Graph Status ===============")
print(graph_state)