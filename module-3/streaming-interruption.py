from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.memory import MemorySaver

# Create llm
model = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Create state
class State(MessagesState):
    summary: str

# Create nodes
def call_model(state: State, config: RunnableConfig):
    summary = state.get("summary", "")

    if summary:
        system_message = f"following is the conversation summary to date: {summary}"

        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    response = model.invoke(messages, config)
    return {"messages": response}

def summarize_conversation(state: State):
    summary = state.get("summary", "")

    if summary:
        
        summary_message = (
            f"This is the summary of the converstaion to date {summary}\n\n"
            "Extend the summary by taking into account following messages below: \n"
        )
    else:
        summary_message = "Create a summary of following conversation: "

    messages = [HumanMessage(content=summary_message)] + state["messages"]
    response = model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

# Create conditional edge logic
def should_continue(state: State):

    messages = state["messages"]

    if len(messages) > 6:
        return "summarize_conversation"
    
    return END

# Define graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile graph
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Evaluate "updates" streaming method
config = {"configurable": {"thread_id": "1"}}

# for chunk in graph.stream({"messages": [HumanMessage(content="hi! I'm Lance")]}, config, stream_mode="updates"):
#     print(chunk)

print("\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-\n")

# for chunk in graph.stream({"messages": [HumanMessage(content="hi! I'm Lance")]}, config, stream_mode="updates"):
#     chunk["conversation"]["messages"].pretty_print()

print("\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-\n")

# Evaluate "values" stream method

config = {"configurable": {"thread_id": "2"}}

# for chunk in graph.stream({"messages": [HumanMessage(content="hi! I'm Lance")]}, config, stream_mode="values"):
#     print(chunk)

print("\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-\n")

input_message = HumanMessage(content="hi! I'm Lance")
for event in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    for m in event["messages"]:
        m.pretty_print()
    print("---"*25)

print("\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-\n")

# Evaluate streaming tokens

config = {"configurable": {"thread_id": "3"}}

input_message = HumanMessage(content="Tell me about the 49ers NFL team")
async for event in graph.astream_events({"messages": [input_message]}, config, version="v2"):
    print(f"Node: {event["metadata"].get("langgraph_node","")}. Type: {event["event"]}. Name: {event["name"]}")

print("\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-\n")