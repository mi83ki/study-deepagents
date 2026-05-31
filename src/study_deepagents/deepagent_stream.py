import os
from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

load_dotenv()


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's always sunny in {city}!"


model = ChatOpenAI(
    model=os.getenv("LLM_MODEL", ""),  # LMStudio上のモデル名
    base_url=os.getenv("LM_STUDIO_BASE_URL"),
    api_key="lm-studio",  # 何でも OK（LMStudio は検証しない）
    temperature=0.6,
)

weather_agent = create_agent(
    model=model,
    tools=[get_weather],
    name="weather_agent",
)


def call_weather(query: str) -> str:
    """Query the weather agent."""
    result = weather_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].text


supervisor = create_agent(
    model=model,
    tools=[call_weather],
    name="supervisor",
)

stream = supervisor.stream_events(
    {"messages": [{"role": "user", "content": "What's the weather in Boston?"}]},
    version="v3",
)

# for subagent in stream.subgraphs:
#     if subagent.graph_name != "weather_agent":
#         continue
#     print(f"{subagent.graph_name}: ", end="")
#     for message in subagent.messages:
#         for token in message.text:
#             print(token, end="", flush=True)
#     print()

# for message in stream.messages:
#     for delta in message.reasoning:
#         print(f"[thinking] {delta}", end="", flush=True)

#     for delta in message.text:
#         print(delta, end="", flush=True)
# for message in stream.messages:
#     for chunk in message.tool_calls:
#         print(f"tool call chunk: {chunk}")

#     finalized = message.tool_calls.get()
#     if finalized:
#         print(f"finalized tool calls: {finalized}")

for call in stream.tool_calls:
    print(f"{call.tool_name}({call.input})")
    for delta in call.output_deltas:
        print(delta, end="", flush=True)
    print(call.output, call.error)
# for name, item in stream.interleave("messages", "tool_calls", "values"):
#     if name == "messages":
#         print(f"[{name}]{item.text}")
#     elif name == "tool_calls":
#         print(f"[{name}]{item.tool_name}", item.input)
#     # elif name == "values":
#     #     print(f"[{name}]{item}")
#     # elif name == "subagents":
#     #     print(f"[{name}]{item}")


# # for message in stream.messages:
# #     # print(f"[{message.node}] ", end="")
# #     # for delta in message.text:
# #     #     print(delta, end="", flush=True)

# #     # full_message = message.output
# #     # usage = full_message.usage_metadata
# #     # if usage:
# #     #     print(usage)


# for subagent in stream.subgraphs:
#     if subagent.graph_name != "weather_agent":
#         continue
#     print(f"{subagent.graph_name}: ", end="")
#     for message in subagent.messages:
#         for token in message.text:
#             print(token, end="", flush=True)
#     print()

# for message in stream.messages:
#     for delta in message.reasoning:
#         print(f"[thinking] {delta}", end="", flush=True)

#     for delta in message.text:
#         print(delta, end="", flush=True)

#     for chunk in message.tool_calls:
#         print(f"tool call chunk: {chunk}")

#     finalized = message.tool_calls.get()
#     if finalized:
#         print(f"finalized tool calls: {finalized}")

# for call in stream.tool_calls:
#     print(f"{call.tool_name}({call.input})")
#     for delta in call.output_deltas:
#         print(delta, end="", flush=True)
#     print(call.output, call.error)

# final_state = stream.output

# stream = await supervisor.astream_events(input, version="v3")


# async def consume_messages():
#     async for message in stream.messages:
#         print(await message.text)


# async def consume_tool_calls():
#     async for call in stream.tool_calls:
#         print(call.tool_name, call.input)


# await asyncio.gather(consume_messages(), consume_tool_calls())
