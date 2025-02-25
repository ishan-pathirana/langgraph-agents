from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, trim_messages
from langgraph.graph import StateGraph, MessagesState, START, END

# Define LLM
llm = ChatOpenAI(model="gpt-4o-mini")

## Messages as state

# Define messages
messages =  [AIMessage(f"So you said you were researching ocean mammals?", name="Bot")]
messages.append(HumanMessage(f"Yes, I know about whatles. But what others should I learn about?",  name="Lance"))

for m in messages:
    m.pretty_print()

print("\n====== CHAT MODEL GRAPH =====\n")

# Define node
def chat_model_node(state: MessagesState):
    return {"messages": llm.invoke(state["messages"])}

# Build graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("chat_model_node", chat_model_node)

# Add edges
builder.add_edge(START, "chat_model_node")
builder.add_edge("chat_model_node", END)

# Compile graph
graph = builder.compile()

# Get output
output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()

print("\n====== REDUCE MESSAGES USING RemoveMessage =====\n")

## Reducer to filter messages

# Define nodes

def filter_messages(state: MessagesState):
    delete_meassages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_meassages}

def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("filter_messages", filter_messages)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "filter_messages")
builder.add_edge("filter_messages", "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# Define messages
messages = [AIMessage("Hi", name="Bot", id="1")]
messages.append(HumanMessage("Hi", name="Lance", id="2"))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id="4"))

# Invoke graph
output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()

print("\n====== FILTER MESSAGES WHILE KEEPING MESSAGE STATE =====\n")

## Filtering messages

# Define node
def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"][-1:])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# Add last reply from last conversation and add other messages
messages.append(output["messages"][-1])
messages.append(HumanMessage("Tell me more about Narwhals!", name="Lance"))

# Invoke using message filtering
output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()

print("\n====== TRIM MESSAGES =====\n")

# Define node
def chat_model_node(state: MessagesState):
    messages = trim_messages(
        state["messages"],
        max_tokens=100,
        strategy="last",
        token_counter=ChatOpenAI(model="gpt-4o-mini"),
        allow_partial=False
    )
    return {"messages": [llm.invoke(messages)]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# Add messages to messages list
messages.append(output["messages"][-1])
messages.append(HumanMessage("Tell me where Orcas live!", name="Lance"))

print("\n====== EXAMPLE OUTPUT OF TRIM MESSAGES =====\n")

print(trim_messages(
    messages,
    max_tokens=100,
    strategy="last",
    token_counter=ChatOpenAI(model="gpt-4o-mini"),
    allow_partial=False
))

print("\n====== TRIM MESSAGE LLM INVOCATION =====\n")

messages_out_trim = graph.invoke({"messages": messages})
for m in messages_out_trim["messages"]:
    m.pretty_print()