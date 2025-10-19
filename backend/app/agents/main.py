from agents import Runner, set_tracing_disabled, SQLiteSession
from backend.app.agents.my_agents.assistant_agent import agent
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from backend.app.services.agent_service import PostgresSession
from backend.app.db.main import get_session
import uuid

set_tracing_disabled(True)

async def agent_stream_generator(prompt: str, conversation_id: str | None = None):
    """Async generator to yield chunks from the Agent SDK and store history in Postgres."""

    # If no conversation_id is provided, generate a new one
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    # Get a database session
    async for db_session in get_session():
        # Create a PostgresSession to store agent chat history
        agent_session = PostgresSession(db_session, conversation_id)

        # Pass the custom session to Runner
        result = Runner.run_streamed(
            agent,
            input=prompt,
            session=agent_session,   # ✅ use Postgres-backed session
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent) and event.data.delta:
                    # Stream the agent's response back to the client
                    yield event.data.delta

            elif event.type == "run_item_stream_event" and event.name == "tool_called":
                print(f"Agent called tool: {event.item.name}")

