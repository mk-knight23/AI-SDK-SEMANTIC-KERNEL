"""
Text processing plugin for Semantic Kernel.

Provides text manipulation and analysis capabilities.
"""

import re
import hashlib
from typing import List, Optional

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from app.plugins.base import BasePlugin, PluginMetadata


class TextPlugin(BasePlugin):
    """
    Plugin for text processing operations.

    Provides common text manipulation and analysis functions.
    """

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="text",
            description="Provides text manipulation and analysis capabilities",
            version="1.0.0",
            author="AI-SDK-SEMANTIC-KERNEL"
        )

    @kernel_function(
        description="Convert text to uppercase",
        name="to_upper"
    )
    def to_upper(self, text: str) -> str:
        """Convert text to uppercase."""
        return text.upper()

    @kernel_function(
        description="Convert text to lowercase",
        name="to_lower"
    )
    def to_lower(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()

    @kernel_function(
        description="Capitalize the first letter of each word",
        name="capitalize"
    )
    def capitalize(self, text: str) -> str:
        """Capitalize the first letter of each word."""
        return text.title()

    @kernel_function(
        description="Reverse the text",
        name="reverse"
    )
    def reverse(self, text: str) -> str:
        """Reverse the text."""
        return text[::-1]

    @kernel_function(
        description="Count the number of words in text",
        name="word_count"
    )
    def word_count(self, text: str) -> str:
        """Count the number of words."""
        words = text.strip().split()
        return str(len(words))

    @kernel_function(
        description="Count the number of characters in text",
        name="char_count"
    )
    def char_count(self, text: str) -> str:
        """Count the number of characters."""
        return str(len(text))

    @kernel_function(
        description="Count the number of characters excluding spaces",
        name="char_count_no_spaces"
    )
    def char_count_no_spaces(self, text: str) -> str:
        """Count characters excluding spaces."""
        return str(len(text.replace(" ", "")))

    @kernel_function(
        description="Extract all email addresses from text",
        name="extract_emails"
    )
    def extract_emails(self, text: str) -> str:
        """Extract email addresses from text."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text, re.IGNORECASE)
        if emails:
            return "; ".join(set(emails))
        return "No emails found"

    @kernel_function(
        description="Extract all URLs from text",
        name="extract_urls"
    )
    def extract_urls(self, text: str) -> str:
        """Extract URLs from text."""
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(pattern, text)
        if urls:
            return "; ".join(set(urls))
        return "No URLs found"

    @kernel_function(
        description="Extract all phone numbers from text",
        name="extract_phones"
    )
    def extract_phones(self, text: str) -> str:
        """Extract phone numbers from text."""
        pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\(\d{3}\)\s*\d{3}[-.]?\d{4}'
        phones = re.findall(pattern, text)
        if phones:
            return "; ".join(set(phones))
        return "No phone numbers found"

    @kernel_function(
        description="Generate a hash of the text",
        name="hash_text"
    )
    def hash_text(self, text: str, algorithm: str = "sha256") -> str:
        """Generate a hash of the text."""
        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }

        algo = algorithms.get(algorithm.lower(), hashlib.sha256)
        return algo(text.encode()).hexdigest()

    @kernel_function(
        description="Remove extra whitespace from text",
        name="normalize_whitespace"
    )
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        return " ".join(text.split())

    @kernel_function(
        description="Remove all special characters from text",
        name="remove_special_chars"
    )
    def remove_special_chars(self, text: str) -> str:
        """Remove special characters, keeping only alphanumeric and spaces."""
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)

    @kernel_function(
        description="Check if text contains a specific word",
        name="contains_word"
    )
    def contains_word(self, text: str, word: str) -> str:
        """Check if text contains a specific word."""
        pattern = r'\b' + re.escape(word) + r'\b'
        found = bool(re.search(pattern, text, re.IGNORECASE))
        return f"Yes, '{word}' found in text" if found else f"No, '{word}' not found in text"

    @kernel_function(
        description="Find and replace text",
        name="find_replace"
    )
    def find_replace(self, text: str, find: str, replace: str) -> str:
        """Find and replace text."""
        return text.replace(find, replace)

    @kernel_function(
        description="Split text into chunks of specified size",
        name="chunk_text"
    )
    def chunk_text(self, text: str, chunk_size: int = 100) -> str:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return "\n\n--- Chunk Boundary ---\n\n".join(chunks)

    @kernel_function(
        description="Truncate text to a maximum length",
        name="truncate"
    )
    def truncate(self, text: str, max_length: int, add_ellipsis: bool = True) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]
        if add_ellipsis:
            truncated = truncated[:max_length - 3] + "..."
        return truncated

    @kernel_function(
        description="Generate a summary by extracting the first and last sentences",
        name="extract_summary"
    )
    def extract_summary(self, text: str) -> str:
        """Extract a simple summary from text."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= 2:
            return text.strip()

        first = sentences[0]
        last = sentences[-1]

        return f"Summary: {first}. ... {last}."

    @kernel_function(
        description="Calculate the readability score (approximate)",
        name="readability_score"
    )
    def readability_score(self, text: str) -> str:
        """
        Calculate approximate readability using a simplified formula.
        Returns grade level approximation.
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = text.split()

        if not sentences or not words:
            return "Unable to calculate score"

        avg_sentence_length = len(words) / len(sentences)

        # Simplified Flesch Reading Ease approximation
        # This is a rough approximation
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (sum(1 for w in words if len(w) > 6) / len(words)))

        if score > 90:
            level = "5th grade"
        elif score > 80:
            level = "6th grade"
        elif score > 70:
            level = "7th grade"
        elif score > 60:
            level = "8th-9th grade"
        elif score > 50:
            level = "10th-12th grade"
        elif score > 30:
            level = "College level"
        else:
            level = "Professional/Graduate level"

        return f"Readability: {level} (Score: {score:.1f})"
