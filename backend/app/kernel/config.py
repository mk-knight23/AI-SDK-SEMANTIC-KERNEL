"""
Semantic Kernel configuration module.

This module provides kernel configuration with support for multiple
AI providers (OpenAI, Azure OpenAI, Anthropic).
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
from semantic_kernel.connectors.ai.anthropic import AnthropicChatCompletion
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings


class ProviderType(str, Enum):
    """Supported AI provider types."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"


@dataclass
class KernelConfig:
    """Configuration for Semantic Kernel."""
    provider: ProviderType = ProviderType.OPENAI
    model_id: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    endpoint: Optional[str] = None  # For Azure OpenAI
    deployment_name: Optional[str] = None  # For Azure OpenAI
    api_version: str = "2024-02-15-preview"  # For Azure OpenAI
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9

    @classmethod
    def from_env(cls) -> "KernelConfig":
        """
        Create kernel configuration from environment variables.

        Environment variables:
            AI_PROVIDER: Provider type (openai, azure_openai, anthropic)
            AI_MODEL_ID: Model identifier
            AI_API_KEY: API key for the provider
            AI_ENDPOINT: Azure OpenAI endpoint (optional)
            AI_DEPLOYMENT_NAME: Azure OpenAI deployment name (optional)
            AI_API_VERSION: Azure OpenAI API version (optional)
            AI_TEMPERATURE: Temperature for generation (optional)
            AI_MAX_TOKENS: Max tokens for generation (optional)

        Returns:
            KernelConfig instance
        """
        provider = ProviderType(os.getenv("AI_PROVIDER", "openai"))
        api_key = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")

        config = cls(
            provider=provider,
            model_id=os.getenv("AI_MODEL_ID", "gpt-4o-mini"),
            api_key=api_key,
            endpoint=os.getenv("AI_ENDPOINT"),
            deployment_name=os.getenv("AI_DEPLOYMENT_NAME"),
            api_version=os.getenv("AI_API_VERSION", "2024-02-15-preview"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "2000")),
            top_p=float(os.getenv("AI_TOP_P", "0.9"))
        )

        return config

    def get_execution_settings(self) -> PromptExecutionSettings:
        """
        Get prompt execution settings from config.

        Returns:
            PromptExecutionSettings instance
        """
        return PromptExecutionSettings(
            service_id=str(self.provider),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p
        )


class KernelFactory:
    """Factory for creating configured Semantic Kernel instances."""

    @staticmethod
    def create_kernel(config: Optional[KernelConfig] = None) -> Kernel:
        """
        Create a Semantic Kernel instance with the given configuration.

        Args:
            config: Kernel configuration. If None, loads from environment.

        Returns:
            Configured Kernel instance

        Raises:
            ValueError: If configuration is invalid or API key is missing
        """
        if config is None:
            config = KernelConfig.from_env()

        if not config.api_key:
            raise ValueError(
                "API key is required. Set AI_API_KEY or OPENAI_API_KEY environment variable."
            )

        kernel = Kernel()

        # Add chat completion service based on provider
        service = KernelFactory._create_chat_service(config)
        kernel.add_service(service)

        return kernel

    @staticmethod
    def _create_chat_service(config: KernelConfig) -> ChatCompletionClientBase:
        """
        Create a chat completion service based on provider type.

        Args:
            config: Kernel configuration

        Returns:
            ChatCompletionClientBase instance

        Raises:
            ValueError: If provider is not supported
        """
        execution_settings = config.get_execution_settings()

        if config.provider == ProviderType.OPENAI:
            return OpenAIChatCompletion(
                service_id=str(config.provider),
                ai_model_id=config.model_id,
                api_key=config.api_key,
                execution_settings=execution_settings
            )

        elif config.provider == ProviderType.AZURE_OPENAI:
            if not config.endpoint:
                raise ValueError("Azure OpenAI endpoint is required for Azure provider")

            return AzureChatCompletion(
                service_id=str(config.provider),
                deployment_name=config.deployment_name or config.model_id,
                endpoint=config.endpoint,
                api_key=config.api_key,
                api_version=config.api_version,
                execution_settings=execution_settings
            )

        elif config.provider == ProviderType.ANTHROPIC:
            return AnthropicChatCompletion(
                service_id=str(config.provider),
                ai_model_id=config.model_id,
                api_key=config.api_key,
                execution_settings=execution_settings
            )

        else:
            raise ValueError(f"Unsupported provider: {config.provider}")


# Global kernel instance
_kernel: Optional[Kernel] = None


def get_kernel(config: Optional[KernelConfig] = None) -> Kernel:
    """
    Get or create the global kernel instance.

    Args:
        config: Optional kernel configuration. Only used on first call.

    Returns:
        Kernel instance
    """
    global _kernel
    if _kernel is None:
        _kernel = KernelFactory.create_kernel(config)
    return _kernel


def reset_kernel() -> None:
    """Reset the global kernel instance (useful for testing)."""
    global _kernel
    _kernel = None
