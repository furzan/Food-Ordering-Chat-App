from typing import List, Dict, Any, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, delete
from backend.app.db.models.conversation_msg_model import ConversationMessage

class PostgresSession:
    def __init__(self, db: AsyncSession, conversation_id: str):
        self.db = db
        self.conversation_id = conversation_id

    async def get_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve messages in the format expected by the OpenAI Agents SDK."""
        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == self.conversation_id)
            .order_by(ConversationMessage.created_at.asc())
        )
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        rows = result.scalars().all()

        # Return messages in the SDK's expected format
        messages = []
        for row in rows:
            msg = {"role": row.role}
            
            # Handle content - could be dict or string
            if isinstance(row.content, dict):
                if "text" in row.content:
                    msg["content"] = row.content["text"]
                else:
                    # If it's a dict but not the simple format, keep it as is
                    msg["content"] = row.content
            else:
                msg["content"] = str(row.content)
            
            messages.append(msg)
        
        return messages

    async def add_items(self, items: List[Dict[str, Any]]) -> None:
        """Store messages from the OpenAI Agents SDK."""
        for item in items:
            role = item.get("role")
            content = item.get("content")
            
            if not role or role in (None, {"text": "None"}):
                continue
            
            # Normalize content storage
            if isinstance(content, str):
                content_to_store = {"text": content}
            elif isinstance(content, dict):
                # If already a dict, check if it has text or store as is
                if "text" in content:
                    content_to_store = {"text": content["text"]}
                else:
                    # Store the whole dict (might contain other fields)
                    content_to_store = content
            elif isinstance(content, list):
                # Handle list of content parts (multimodal messages)
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                    elif isinstance(part, str):
                        text_parts.append(part)
                content_to_store = {"text": " ".join(text_parts) if text_parts else str(content)}
            else:
                content_to_store = {"text": str(content)}

            new_msg = ConversationMessage(
                conversation_id=self.conversation_id,
                role=role,
                content=content_to_store
            )
            self.db.add(new_msg)
        
        await self.db.commit()

    async def pop_item(self) -> Optional[Dict[str, Any]]:
        """Remove and return the last message."""
        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == self.conversation_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(1)
        )
        row = result.scalars().first()
        if not row:
            return None

        await self.db.delete(row)
        await self.db.commit()

        # Return in SDK format
        msg = {"role": row.role}
        if isinstance(row.content, dict) and "text" in row.content:
            msg["content"] = row.content["text"]
        else:
            msg["content"] = str(row.content)
        
        return msg

    async def clear_session(self) -> None:
        """Clear all messages for this conversation."""
        await self.db.execute(
            delete(ConversationMessage).where(
                ConversationMessage.conversation_id == self.conversation_id
            )
        )
        await self.db.commit()