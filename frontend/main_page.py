import chainlit as cl
import httpx
from typing import Optional
import os

# Configure your API endpoint here
base_url  = os.getenv("BASE_SERVER_URL")
AUTH_API_URL = os.getenv("AUTH_API_URL", "http://http://127.0.0.1:8000/api/v1/user/login")

@cl.password_auth_callback
async def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """
    This function is called when a user tries to sign in.
    It calls your predefined API to authenticate the user.
    
    Returns:
        - cl.User object if authentication is successful
        - None if authentication fails
    """
    try:
        # Call your authentication API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                AUTH_API_URL,
                data={
                    "username": username,
                    "password": password
                }
            )
            
            # Check if authentication was successful
            if response.status_code == 200:
            # if True:
                data = response.json()
                
                # Create and return a Chainlit User object
                return cl.User(
                    identifier=username,
                    # metadata={
                    #     "role": data.get("role", "user"),
                    #     "email": data.get("email", ""),
                    #     "token": data.get("token", ""),
                    #     # Add any other user metadata from your API response
                    # }
                )
            else:
                # Authentication failed - log the error
                print(f"Authentication failed: {response.status_code}")
                if response.status_code != 401:
                    print(f"Response: {response.text}")
                return None
                
    except httpx.ConnectError:
        print(f"Could not connect to authentication API at {AUTH_API_URL}")
        print("Make sure your authentication server is running.")
        return None
    except httpx.TimeoutException:
        print("Authentication API timeout")
        return None
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None


@cl.on_chat_start
async def start():
    """
    This function is called when the chat starts (after successful authentication).
    Only authenticated users will reach this point.
    """
    user = cl.user_session.get("user")
    
    # Display welcome message
    await cl.Message(
        content=f"Welcome back, **{user.identifier}**! 👋\n\nHow can I help you today?"
    ).send()
    
    # Store user info in session for later use
    cl.user_session.set("username", user.identifier)



@cl.on_message
async def main(message: cl.Message):
    """
    This function is called every time a user sends a message.
    It now streams the response from the FastAPI backend to the Chainlit frontend.
    """
    # Note: user is available via cl.user_session.get("user") but is unused for streaming logic.
    
    # 1. Create a message object and send it immediately to reserve its spot
    msg = cl.Message(content="")
    await msg.send()
    
    payload = {
        "message": message.content,
    }
    
    try:
        # Use httpx.AsyncClient for async requests
        # Set timeout to None or a very high value for long-running streams
        async with httpx.AsyncClient(timeout=None) as client:
            
            # 2. Use client.stream() and async with to manage the response stream
            async with client.stream(
                "POST", 
                base_url + '/message',
                json=payload,
            ) as response:
                
                # Check for an immediate non-streaming error
                if response.status_code != 200:
                    # Read the error body completely if the request failed
                    error_text = await response.aread()
                    raise Exception(f"API Error {response.status_code}: {error_text.decode()}")

                # 3. Iterate over the stream chunk-by-chunk
                async for chunk in response.aiter_bytes():
                    # Decode the bytes chunk to a string token
                    token = chunk.decode("utf-8")
                    
                    # 4. Stream the token to the Chainlit message for real-time display
                    # This updates the message content on the UI incrementally
                    await msg.stream_token(token)

        # 5. Streaming is complete. Call update() to finalize the message.
        # The content is already set by stream_token, so we just call update().
        await msg.update()

    except Exception as e:
        # Handle exceptions (e.g., connection errors, invalid URLs)
        error_content = f"An error occurred while streaming: {str(e)}"
        
        # Remove the incomplete message and send a new error message
        await msg.remove() 
        await cl.Message(
            content=error_content, 
            author="Error"
        ).send()


@cl.on_chat_end
async def end():
    """
    This function is called when the chat session ends.
    """
    user = cl.user_session.get("user")
    if user:
        print(f"Chat session ended for user: {user.identifier}")


@cl.on_logout
async def on_logout(user: cl.User):
    """
    This function is called when a user logs out.
    """
    print(f"User {user.identifier} logged out")