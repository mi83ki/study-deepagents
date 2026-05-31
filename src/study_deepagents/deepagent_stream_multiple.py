import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

load_dotenv()


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


async def main():
    """スーパーバイザーエージェントを非同期でストリーミング実行する。"""
    input = {"messages": [{"role": "user", "content": "What's the weather in Boston?"}]}
    stream = await supervisor.astream_events(input, version="v3")

    async def consume_messages():
        async for message in stream.messages:
            async for delta in message.reasoning:
                print(f"[thinking] {delta}", end="", flush=True)
            async for delta in message.text:
                print(delta, end="", flush=True)

    async def consume_tool_calls():
        async for call in stream.tool_calls:
            print(call.tool_name, call.input)

    async def consume_subagents():
        async for subagent in stream.subgraphs:
            # if subagent.graph_name != "weather_agent":
            #     continue
            print(f"{subagent.graph_name}: ", end="")
            async for message in subagent.messages:
                async for token in message.text:
                    print(token, end="", flush=True)
            print()

    await asyncio.gather(consume_messages(), consume_tool_calls(), consume_subagents())


asyncio.run(main())
