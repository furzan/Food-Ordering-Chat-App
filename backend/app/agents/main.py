from agents import Runner, set_tracing_disabled, SQLiteSession
from my_agents.assistant_agent import agent
from openai.types.responses import ResponseTextDeltaEvent
import asyncio

set_tracing_disabled(True)

session = SQLiteSession("user1", "./db/conversation1.db" )

async def clear_session_data():
    await session.clear_session()

async def get_session_data():
    user_data = await session.get_items()
    for user in user_data:
        print (f"{user['role']}: {user['content']}")

# asyncio.run(clear_session_data())    

# asyncio.run(get_session_data())

# while True:

#     prompt = input ('write prompt here: ')
#     if prompt == 'exit':
#         break

#     res = Runner.run_sync(
#         starting_agent= agent,
#         input= prompt,
#         session=session)

#     print(res.final_output)

async def main():
    while True:
        prompt = input ('\n|| write prompt here: ')
        if prompt == 'exit':
            break

        res = Runner.run_streamed(
            starting_agent= agent,
            input= prompt,
            session=session)
        async for event in res.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)


 
if __name__ == "__main__":
    asyncio.run(main())

