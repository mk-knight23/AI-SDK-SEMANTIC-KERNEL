"""
Memory store for Semantic Kernel.

Provides conversation memory and context management for AI interactions.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, asdict
from threading import Lock

from pydantic import BaseModel, Field


class MessageRole(str):
    """Message role types."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class Message:
    """A single message in a conversation."""
    id: str
    role: str
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {})
        )


@dataclass
class Conversation:
    """A conversation with multiple messages."""
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            messages=[Message.from_dict(m) for m in data["messages"]],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            metadata=data.get("metadata", {})
        )


class MemoryStore:
    """
    In-memory store for conversations and context.

    Provides thread-safe operations for managing conversation history,
    context, and metadata.
    """

    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}
        self._lock = Lock()
        self._semantic_memory: Dict[str, Any] = {}
        self._volatile_memory: Dict[str, Any] = {}

    def create_conversation(
        self,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            title: Optional title for the conversation
            metadata: Optional metadata dictionary

        Returns:
            Created Conversation
        """
        conv_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        if title is None:
            title = f"Conversation {conv_id[:8]}"

        conversation = Conversation(
            id=conv_id,
            title=title,
            messages=[],
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )

        with self._lock:
            self._conversations[conv_id] = conversation

        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Conversation or None if not found
        """
        with self._lock:
            return self._conversations.get(conversation_id)

    def list_conversations(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List all conversations.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversations
        """
        with self._lock:
            convs = sorted(
                self._conversations.values(),
                key=lambda c: c.updated_at,
                reverse=True
            )
            return convs[offset:offset + limit]

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: ID of the conversation to delete

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                return True
            return False

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """
        Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation
            role: Message role (user, assistant, system, function)
            content: Message content
            metadata: Optional metadata

        Returns:
            Created Message or None if conversation not found
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                return None

            message = Message(
                id=str(uuid.uuid4()),
                role=role,
                content=content,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata=metadata or {}
            )

            conversation.messages.append(message)
            conversation.updated_at = datetime.now(timezone.utc).isoformat()

            return message

    def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get messages from a conversation.

        Args:
            conversation_id: ID of the conversation
            limit: Optional limit on number of messages

        Returns:
            List of messages
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                return []

            messages = conversation.messages
            if limit is not None:
                messages = messages[-limit:]

            return messages

    def update_conversation_title(
        self,
        conversation_id: str,
        title: str
    ) -> bool:
        """
        Update the title of a conversation.

        Args:
            conversation_id: ID of the conversation
            title: New title

        Returns:
            True if updated, False if not found
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                return False

            conversation.title = title
            conversation.updated_at = datetime.now(timezone.utc).isoformat()
            return True

    # Semantic Memory Operations (for long-term storage of facts)

    def set_semantic(self, key: str, value: Any) -> None:
        """
        Store a value in semantic memory.

        Args:
            key: Storage key
            value: Value to store
        """
        with self._lock:
            self._semantic_memory[key] = value

    def get_semantic(self, key: str) -> Optional[Any]:
        """
        Get a value from semantic memory.

        Args:
            key: Storage key

        Returns:
            Stored value or None
        """
        with self._lock:
            return self._semantic_memory.get(key)

    def delete_semantic(self, key: str) -> bool:
        """
        Delete a value from semantic memory.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._semantic_memory:
                del self._semantic_memory[key]
                return True
            return False

    def list_semantic_keys(self) -> List[str]:
        """
        List all keys in semantic memory.

        Returns:
            List of keys
        """
        with self._lock:
            return list(self._semantic_memory.keys())

    # Volatile Memory Operations (for session-specific data)

    def set_volatile(self, key: str, value: Any) -> None:
        """
        Store a value in volatile memory.

        Args:
            key: Storage key
            value: Value to store
        """
        with self._lock:
            self._volatile_memory[key] = value

    def get_volatile(self, key: str) -> Optional[Any]:
        """
        Get a value from volatile memory.

        Args:
            key: Storage key

        Returns:
            Stored value or None
        """
        with self._lock:
            return self._volatile_memory.get(key)

    def delete_volatile(self, key: str) -> bool:
        """
        Delete a value from volatile memory.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._volatile_memory:
                del self._volatile_memory[key]
                return True
            return False

    def clear_volatile(self) -> None:
        """Clear all volatile memory."""
        with self._lock:
            self._volatile_memory.clear()

    # Export/Import

    def export_conversation(self, conversation_id: str) -> Optional[str]:
        """
        Export a conversation as JSON.

        Args:
            conversation_id: ID of the conversation

        Returns:
            JSON string or None if not found
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                return None

            return json.dumps(conversation.to_dict(), indent=2)

    def import_conversation(self, json_data: str) -> Optional[Conversation]:
        """
        Import a conversation from JSON.

        Args:
            json_data: JSON string

        Returns:
            Imported Conversation or None if invalid
        """
        try:
            data = json.loads(json_data)
            conversation = Conversation.from_dict(data)

            with self._lock:
                self._conversations[conversation.id] = conversation

            return conversation
        except Exception:
            return None


# Global memory store instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """
    Get the global memory store instance.

    Returns:
        MemoryStore instance
    """
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store


def reset_memory_store() -> None:
    """Reset the global memory store (useful for testing)."""
    global _memory_store
    _memory_store = None
