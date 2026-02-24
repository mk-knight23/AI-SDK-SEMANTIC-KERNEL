"""
Flask API routes for Semantic Kernel application.

Provides REST API endpoints for chat, plugins, memory, and planning.
"""

import json
import asyncio
from functools import wraps
from typing import Any, Dict, List

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.kernel.config import get_kernel, KernelConfig
from app.memory.store import get_memory_store, MessageRole
from app.plugins.base import get_plugin_registry
from app.plugins.time_plugin import TimePlugin
from app.plugins.calculator_plugin import CalculatorPlugin
from app.plugins.weather_plugin import WeatherPlugin
from app.plugins.text_plugin import TextPlugin
from app.planners.stepwise import create_stepwise_planner
from app.planners.sequential import create_sequential_planner
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    PluginInfo,
    PluginsListResponse,
    PluginFunctionInvokeRequest,
    PluginFunctionInvokeResponse,
    ConversationCreateRequest,
    ConversationResponse,
    ConversationsListResponse,
    MessagesListResponse,
    MessageAddRequest,
    SemanticMemorySetRequest,
    SemanticMemoryGetResponse,
    PlannerRequest,
    PlannerResponse,
    HealthResponse,
    KernelStatusResponse,
    ErrorResponse,
)


# Create Blueprint
api_bp = Blueprint('api', __name__)


# Helper functions

def validate_json(schema_class):
    """Decorator to validate JSON request against a Pydantic schema."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json() or {}
                validated = schema_class(**data)
                return f(validated, *args, **kwargs)
            except ValidationError as e:
                return jsonify({
                    "error": "Validation error",
                    "detail": e.errors()
                }), 400
        return wrapper
    return decorator


def async_route(f):
    """Decorator to run async functions in Flask."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(f(*args, **kwargs))
            return result
        finally:
            loop.close()
    return wrapper


def run_async(coro):
    """Helper to run async function."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Initialization

def initialize_plugins():
    """Initialize and register all plugins."""
    registry = get_plugin_registry()

    plugins = [
        TimePlugin(),
        CalculatorPlugin(),
        WeatherPlugin(),
        TextPlugin(),
    ]

    for plugin in plugins:
        try:
            registry.register(plugin)
        except ValueError:
            pass  # Already registered

    return registry


def initialize_kernel():
    """Initialize Semantic Kernel with plugins."""
    try:
        kernel = get_kernel()
        registry = initialize_plugins()

        # Register plugins with kernel
        for plugin_name in [p.name for p in registry.list_plugins()]:
            plugin = registry.get_plugin(plugin_name)
            if plugin:
                kernel.add_plugin(plugin, plugin_name)

        return kernel
    except ValueError as e:
        # Kernel not configured (no API key)
        return None


# Routes

@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(HealthResponse().model_dump()), 200


@api_bp.route("/status", methods=["GET"])
def kernel_status():
    """Get kernel status and configuration."""
    try:
        kernel = initialize_kernel()
        memory = get_memory_store()

        # Check if kernel is configured
        configured = kernel is not None

        # Get configuration
        config = KernelConfig.from_env()

        # Get plugin count
        registry = get_plugin_registry()
        plugins_loaded = len(registry.list_plugins())

        # Get conversation count
        conversations = memory.list_conversations(limit=1000)

        response = KernelStatusResponse(
            configured=configured,
            provider=config.provider.value if configured else None,
            model=config.model_id if configured else None,
            plugins_loaded=plugins_loaded,
            conversations_count=len(conversations)
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to get status",
            "detail": str(e)
        }), 500


@api_bp.route("/chat", methods=["POST"])
@validate_json(ChatRequest)
def chat_completion(request_data: ChatRequest):
    """Handle chat completion with optional function calling."""
    try:
        kernel = initialize_kernel()
        if kernel is None:
            return jsonify({
                "error": "Kernel not configured",
                "detail": "AI_API_KEY environment variable not set"
            }), 500

        memory = get_memory_store()

        # Get or create conversation
        conv_id = request_data.conversation_id
        if conv_id:
            conversation = memory.get_conversation(conv_id)
            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404
        else:
            conversation = memory.create_conversation()

        # Add user message
        memory.add_message(
            conversation.id,
            MessageRole.USER,
            request_data.message
        )

        # Get conversation history for context
        messages = memory.get_messages(conversation.id, limit=10)

        # Build prompt
        history = "\n".join([
            f"{m.role}: {m.content}"
            for m in messages
        ])

        # Generate response
        try:
            result = run_async(kernel.invoke_prompt(
                prompt=f"{history}\nassistant:",
                service_id="openai"
            ))

            assistant_message = str(result)

        except Exception as e:
            assistant_message = f"I apologize, but I encountered an error: {str(e)}"

        # Add assistant message
        msg = memory.add_message(
            conversation.id,
            MessageRole.ASSISTANT,
            assistant_message
        )

        response = ChatResponse(
            conversation_id=conversation.id,
            message_id=msg.id if msg else "",
            content=assistant_message,
            function_calls=None
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Chat completion failed",
            "detail": str(e)
        }), 500


@api_bp.route("/plugins", methods=["GET"])
def list_plugins():
    """List all available plugins."""
    try:
        registry = get_plugin_registry()
        plugins_metadata = registry.list_plugins()

        plugins = [
            PluginInfo(
                name=pm.name,
                description=pm.description,
                version=pm.version,
                author=pm.author,
                functions=pm.functions
            )
            for pm in plugins_metadata
        ]

        response = PluginsListResponse(plugins=plugins)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to list plugins",
            "detail": str(e)
        }), 500


@api_bp.route("/plugins/invoke", methods=["POST"])
@validate_json(PluginFunctionInvokeRequest)
def invoke_plugin_function(request_data: PluginFunctionInvokeRequest):
    """Invoke a specific plugin function."""
    try:
        kernel = initialize_kernel()
        if kernel is None:
            return jsonify({
                "error": "Kernel not configured"
            }), 500

        # Get the plugin
        plugin = kernel.plugins.get(request_data.plugin)
        if not plugin:
            return jsonify({
                "error": f"Plugin '{request_data.plugin}' not found"
            }), 404

        # Get the function
        func = plugin.get(request_data.function)
        if not func:
            return jsonify({
                "error": f"Function '{request_data.function}' not found in plugin '{request_data.plugin}'"
            }), 404

        # Invoke the function
        try:
            result = run_async(func(**request_data.parameters))

            response = PluginFunctionInvokeResponse(
                success=True,
                result=str(result)
            )
            return jsonify(response.model_dump()), 200

        except Exception as e:
            response = PluginFunctionInvokeResponse(
                success=False,
                error=str(e)
            )
            return jsonify(response.model_dump()), 400

    except Exception as e:
        return jsonify({
            "error": "Function invocation failed",
            "detail": str(e)
        }), 500


# Conversation endpoints

@api_bp.route("/conversations", methods=["GET"])
def list_conversations():
    """List all conversations."""
    try:
        memory = get_memory_store()
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        conversations = memory.list_conversations(limit=limit, offset=offset)

        response = ConversationsListResponse(
            conversations=[
                ConversationResponse(
                    id=c.id,
                    title=c.title,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    message_count=len(c.messages),
                    metadata=c.metadata
                )
                for c in conversations
            ],
            total=len(memory.list_conversations(limit=10000))
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to list conversations",
            "detail": str(e)
        }), 500


@api_bp.route("/conversations", methods=["POST"])
@validate_json(ConversationCreateRequest)
def create_conversation(request_data: ConversationCreateRequest):
    """Create a new conversation."""
    try:
        memory = get_memory_store()
        conversation = memory.create_conversation(
            title=request_data.title,
            metadata=request_data.metadata
        )

        response = ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0,
            metadata=conversation.metadata
        )

        return jsonify(response.model_dump()), 201

    except Exception as e:
        return jsonify({
            "error": "Failed to create conversation",
            "detail": str(e)
        }), 500


@api_bp.route("/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id: str):
    """Get a specific conversation."""
    try:
        memory = get_memory_store()
        conversation = memory.get_conversation(conversation_id)

        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        response = ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(conversation.messages),
            metadata=conversation.metadata
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to get conversation",
            "detail": str(e)
        }), 500


@api_bp.route("/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        memory = get_memory_store()
        success = memory.delete_conversation(conversation_id)

        if not success:
            return jsonify({"error": "Conversation not found"}), 404

        return "", 204

    except Exception as e:
        return jsonify({
            "error": "Failed to delete conversation",
            "detail": str(e)
        }), 500


@api_bp.route("/conversations/<conversation_id>/messages", methods=["GET"])
def get_messages(conversation_id: str):
    """Get messages from a conversation."""
    try:
        memory = get_memory_store()
        limit = request.args.get("limit", type=int)

        messages = memory.get_messages(conversation_id, limit=limit)

        response = MessagesListResponse(
            conversation_id=conversation_id,
            messages=[
                ChatMessage(
                    role=m.role,
                    content=m.content,
                    metadata=m.metadata
                )
                for m in messages
            ]
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to get messages",
            "detail": str(e)
        }), 500


@api_bp.route("/conversations/<conversation_id>/messages", methods=["POST"])
@validate_json(MessageAddRequest)
def add_message(conversation_id: str, request_data: MessageAddRequest):
    """Add a message to a conversation."""
    try:
        memory = get_memory_store()
        message = memory.add_message(
            conversation_id,
            request_data.role,
            request_data.content,
            request_data.metadata
        )

        if not message:
            return jsonify({"error": "Conversation not found"}), 404

        return jsonify({
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp
        }), 201

    except Exception as e:
        return jsonify({
            "error": "Failed to add message",
            "detail": str(e)
        }), 500


# Semantic memory endpoints

@api_bp.route("/memory/semantic", methods=["GET"])
def get_semantic_memory():
    """Get a value from semantic memory."""
    try:
        key = request.args.get("key")
        if not key:
            return jsonify({"error": "Key parameter required"}), 400

        memory = get_memory_store()
        value = memory.get_semantic(key)

        response = SemanticMemoryGetResponse(
            key=key,
            value=value,
            found=(value is not None)
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to get semantic memory",
            "detail": str(e)
        }), 500


@api_bp.route("/memory/semantic", methods=["POST"])
@validate_json(SemanticMemorySetRequest)
def set_semantic_memory(request_data: SemanticMemorySetRequest):
    """Set a value in semantic memory."""
    try:
        memory = get_memory_store()
        memory.set_semantic(request_data.key, request_data.value)

        return jsonify({
            "key": request_data.key,
            "stored": True
        }), 201

    except Exception as e:
        return jsonify({
            "error": "Failed to set semantic memory",
            "detail": str(e)
        }), 500


@api_bp.route("/memory/semantic", methods=["DELETE"])
def delete_semantic_memory():
    """Delete a value from semantic memory."""
    try:
        key = request.args.get("key")
        if not key:
            return jsonify({"error": "Key parameter required"}), 400

        memory = get_memory_store()
        success = memory.delete_semantic(key)

        if not success:
            return jsonify({"error": "Key not found"}), 404

        return "", 204

    except Exception as e:
        return jsonify({
            "error": "Failed to delete semantic memory",
            "detail": str(e)
        }), 500


@api_bp.route("/memory/semantic/keys", methods=["GET"])
def list_semantic_keys():
    """List all keys in semantic memory."""
    try:
        memory = get_memory_store()
        keys = memory.list_semantic_keys()

        return jsonify({"keys": keys}), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to list semantic memory keys",
            "detail": str(e)
        }), 500


# Planner endpoints

@api_bp.route("/planner/plan", methods=["POST"])
@validate_json(PlannerRequest)
def create_and_execute_plan(request_data: PlannerRequest):
    """Create and optionally execute a plan."""
    try:
        kernel = initialize_kernel()
        if kernel is None:
            return jsonify({
                "error": "Kernel not configured"
            }), 500

        # Get available functions
        registry = get_plugin_registry()

        # Select planner
        if request_data.planner_type == "sequential":
            planner = create_sequential_planner(kernel)
        else:
            planner = create_stepwise_planner(kernel)

        # Create plan
        plan = run_async(planner.create_plan(
            goal=request_data.goal,
            context=request_data.context
        ))

        results = None
        status = plan.status

        # Execute if requested
        if request_data.execute and plan.steps:
            if request_data.planner_type == "sequential":
                execution = run_async(planner.execute_plan(plan))
            else:
                execution = run_async(planner.execute_plan(plan, max_steps=request_data.max_steps or 10))

            results = execution.get("results", [])
            status = plan.status

        response = PlannerResponse(
            goal=request_data.goal,
            planner_type=request_data.planner_type,
            plan=plan.to_dict() if plan else None,
            results=results,
            status=status,
            final_result=plan.result
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            "error": "Planning failed",
            "detail": str(e)
        }), 500


@api_bp.route("/planner/think", methods=["POST"])
def think_and_act():
    """Execute stepwise think-and-act planning."""
    try:
        data = request.get_json() or {}
        goal = data.get("goal")
        if not goal:
            return jsonify({"error": "Goal parameter required"}), 400

        kernel = initialize_kernel()
        if kernel is None:
            return jsonify({
                "error": "Kernel not configured"
            }), 500

        planner = create_stepwise_planner(kernel)

        result = run_async(planner.think_and_act(
            goal=goal,
            context=data.get("context"),
            max_iterations=data.get("max_iterations", 5)
        ))

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Think and act failed",
            "detail": str(e)
        }), 500
