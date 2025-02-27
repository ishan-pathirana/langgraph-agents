from pprint import pprint
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.checkpoint.memory import MemorySaver

# Define model
model = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Create a state with summary
class State(MessagesState):
    summary: str

# Define nodes
def call_model(state: State):
    summary = state.get("summary", "")

    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
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
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the convesation above:"

    messages =  state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response, "messages": delete_messages}

def should_continue(state: State):
    """Return the next node to execute"""

    messages = state["messages"]

    if len(messages) > 6:
        return "summarize_conversation"

    return END

# Define a graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

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

input_message = HumanMessage(content="i like Nick Bosa, isn't he t he highest paid defensive player?")
output = graph.invoke({"messages": [input_message]}, config)
output["messages"][-1].pretty_print()

# Check if summary is created
print(graph.get_state(config).values.get("summary", ""))

print("\n\n================ Messages ===============")
print(graph.get_state(config).values.get("messages", ""))