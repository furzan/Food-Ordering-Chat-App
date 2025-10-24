from agents import Agent, Runner, set_tracing_disabled, RunContextWrapper
from agents.mcp import MCPServer, MCPServerStdio
from openai.types.responses import ResponseTextDeltaEvent
from backend.app.db.schemas import usercontext
from backend.app.services.agent_service import PostgresSession
from backend.app.db.main import get_session
from backend.app.agents.my_config.gemini_config import MODEL
from pydantic import BaseModel
import uuid

set_tracing_disabled(True) 

def dynamic_instructions(context: RunContextWrapper[usercontext], agent: Agent[usercontext]) -> str:
    return f"""
            You are a helpful and friendly food-ordering assistant for a chat-based app.

            The user's name is {context.context.username}.
            Your goal is to help them browse the restaurant menu, add or remove items from their cart, update item quantities, and place food orders.

            You can:
            - Show available menu items and their prices.
            - Add an item (and quantity) to the user's cart.
            - Remove or update items in the user's cart.
            - Show the current cart summary.
            - Confirm and place the order when the user is ready.

            Always:
            - Confirm actions before placing the order.
            - Ask clarifying questions if the user’s request is ambiguous.
            - Keep responses concise and focused on helping with food ordering.
            - When showing menu items, always include: item_id, item_name, item_price
            - When showing cart items, always include: item_id, item_name, quantity
            - when adding to cart, check the menu items to find the menu item id
            - when updating cart, check the cart items to find the cart item to update

            Context examples:
            - If the user says "show me the menu", respond with the menu items.
            - If the user says "add 2 burgers", update their cart.
            - If the user says "place my order", confirm the order before finalizing.

            Keep your tone natural, warm, and efficient.
            """

agent = Agent[usercontext](
    name = "food ordering assistant", 
    instructions= dynamic_instructions,
    model= MODEL,
    )


async def agent_stream_generator(prompt: str, conversation_id: str | None = None):

    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        
    user = usercontext(
        username = conversation_id
    )

    # Start the MCP server
    async with MCPServerStdio(
        name="ordering-mcp",
        params={
            "command": "uv",
            "args": ["run", "backend/app/agents/MCP/server.py"],   # path to your MCP server file
        },
        cache_tools_list=True
    ) as mcp_server:

        # List available tools (optional for debugging)
        tools = await mcp_server.list_tools()
        print("🧩 Available MCP Tools:")
        for tool in tools:
            print(f" - {tool.name}")

        # Attach MCP server to agent
        agent.mcp_servers = [mcp_server]

        # Create DB session
        async for db_session in get_session():
            agent_session = PostgresSession(db_session, conversation_id)

            # Run the agent stream
            result = Runner.run_streamed(
                agent,
                input=prompt,
                session=agent_session,
                context= user
            )

            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    if isinstance(event.data, ResponseTextDeltaEvent) and event.data.delta:
                        yield event.data.delta  

                elif event.type == "run_item_stream_event" and event.name == "tool_called":
                    print(f"🛠️ Agent called tool")
