import chainlit as cl
import httpx
from typing import Optional
import os

# Configure your API endpoint here
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
                },
                timeout=10.0
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
    Only authenticated users can send messages.
    """
    user = cl.user_session.get("user")
    
    # Show a loading message
    msg = cl.Message(content="")
    await msg.send()
    
    # Simulate processing (replace with your actual logic)
    response = f"Hello **{user.identifier}**! You said: *{message.content}*\n\nI received your message and I'm here to help!"
    
    # Update the message with the response
    msg.content = response
    await msg.update()


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