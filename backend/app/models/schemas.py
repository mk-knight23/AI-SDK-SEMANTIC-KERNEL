"""
API request and response models for the Semantic Kernel application.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


# Chat Request/Response

class ChatMessage(BaseModel):
    """A chat message."""
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class ChatRequest(BaseModel):
    """Request for chat completion."""
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID")
    message: str = Field(..., description="User message")
    use_plugins: bool = Field(default=True, description="Enable plugin function calling")
    max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")


class ChatResponse(BaseModel):
    """Response from chat completion."""
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    content: str = Field(..., description="Assistant response")
    function_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="Function calls made")


# Plugin Request/Response

class PluginInfo(BaseModel):
    """Information about a plugin."""
    name: str = Field(..., description="Plugin name")
    description: str = Field(..., description="Plugin description")
    version: str = Field(default="1.0.0", description="Plugin version")
    author: Optional[str] = Field(default=None, description="Plugin author")
    functions: List[str] = Field(default_factory=list, description="Function names")


class PluginsListResponse(BaseModel):
    """Response listing available plugins."""
    plugins: List[PluginInfo] = Field(default_factory=list, description="Available plugins")


class PluginFunctionInvokeRequest(BaseModel):
    """Request to invoke a plugin function."""
    plugin: str = Field(..., description="Plugin name")
    function: str = Field(..., description="Function name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Function parameters")


class PluginFunctionInvokeResponse(BaseModel):
    """Response from plugin function invocation."""
    success: bool = Field(..., description="Whether invocation succeeded")
    result: Optional[Any] = Field(default=None, description="Function result")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# Memory Request/Response

class ConversationCreateRequest(BaseModel):
    """Request to create a conversation."""
    title: Optional[str] = Field(default=None, description="Conversation title")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class ConversationResponse(BaseModel):
    """Response with conversation details."""
    id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class ConversationsListResponse(BaseModel):
    """Response listing conversations."""
    conversations: List[ConversationResponse] = Field(default_factory=list, description="Conversations")
    total: int = Field(..., description="Total number of conversations")


class MessagesListResponse(BaseModel):
    """Response listing messages in a conversation."""
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Messages")


class MessageAddRequest(BaseModel):
    """Request to add a message to a conversation."""
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class SemanticMemorySetRequest(BaseModel):
    """Request to set semantic memory."""
    key: str = Field(..., description="Storage key")
    value: Any = Field(..., description="Value to store")


class SemanticMemoryGetResponse(BaseModel):
    """Response from semantic memory get."""
    key: str = Field(..., description="Storage key")
    value: Optional[Any] = Field(default=None, description="Stored value")
    found: bool = Field(..., description="Whether key was found")


# Planner Request/Response

class PlannerRequest(BaseModel):
    """Request to create and/or execute a plan."""
    goal: str = Field(..., description="Goal to achieve")
    planner_type: str = Field(default="stepwise", description="Planner type: stepwise or sequential")
    context: Optional[str] = Field(default=None, description="Optional context")
    execute: bool = Field(default=True, description="Whether to execute the plan")
    max_steps: Optional[int] = Field(default=10, description="Maximum steps for execution")


class PlannerResponse(BaseModel):
    """Response from planner."""
    goal: str = Field(..., description="Goal")
    planner_type: str = Field(..., description="Planner type used")
    plan: Optional[Dict[str, Any]] = Field(default=None, description="The plan")
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Execution results")
    status: str = Field(..., description="Status: pending, in_progress, completed, failed")
    final_result: Optional[str] = Field(default=None, description="Final result if completed")


# Health/Status

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Health status")
    service: str = Field(default="semantic-kernel-backend", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")


# Kernel Status

class KernelStatusResponse(BaseModel):
    """Kernel status response."""
    configured: bool = Field(..., description="Whether kernel is configured")
    provider: Optional[str] = Field(default=None, description="AI provider")
    model: Optional[str] = Field(default=None, description="Model ID")
    plugins_loaded: int = Field(..., description="Number of plugins loaded")
    conversations_count: int = Field(..., description="Number of conversations")
