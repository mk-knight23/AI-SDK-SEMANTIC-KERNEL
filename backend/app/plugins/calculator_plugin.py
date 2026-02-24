"""
Calculator plugin for Semantic Kernel.

Provides mathematical calculation capabilities.
"""

import operator
import re
from typing import Union

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from app.plugins.base import BasePlugin, PluginMetadata


class CalculatorPlugin(BasePlugin):
    """
    Plugin for mathematical calculations.

    Provides basic and advanced mathematical operations.
    """

    # Operation mapping
    OPERATIONS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '**': operator.pow,
        '%': operator.mod,
    }

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="calculator",
            description="Provides mathematical calculation capabilities",
            version="1.0.0",
            author="AI-SDK-SEMANTIC-KERNEL"
        )

    @kernel_function(
        description="Add two numbers together",
        name="add"
    )
    def add(self, a: float, b: float) -> str:
        """
        Add two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum as a string
        """
        try:
            result = a + b
            return str(result)
        except Exception as e:
            return f"Error in addition: {str(e)}"

    @kernel_function(
        description="Subtract b from a",
        name="subtract"
    )
    def subtract(self, a: float, b: float) -> str:
        """
        Subtract b from a.

        Args:
            a: First number
            b: Second number to subtract

        Returns:
            Difference as a string
        """
        try:
            result = a - b
            return str(result)
        except Exception as e:
            return f"Error in subtraction: {str(e)}"

    @kernel_function(
        description="Multiply two numbers",
        name="multiply"
    )
    def multiply(self, a: float, b: float) -> str:
        """
        Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product as a string
        """
        try:
            result = a * b
            return str(result)
        except Exception as e:
            return f"Error in multiplication: {str(e)}"

    @kernel_function(
        description="Divide a by b",
        name="divide"
    )
    def divide(self, a: float, b: float) -> str:
        """
        Divide a by b.

        Args:
            a: Numerator
            b: Denominator

        Returns:
            Quotient as a string
        """
        try:
            if b == 0:
                return "Error: Division by zero"
            result = a / b
            return str(result)
        except Exception as e:
            return f"Error in division: {str(e)}"

    @kernel_function(
        description="Raise a to the power of b",
        name="power"
    )
    def power(self, a: float, b: float) -> str:
        """
        Calculate a to the power of b.

        Args:
            a: Base
            b: Exponent

        Returns:
            Result as a string
        """
        try:
            result = a ** b
            return str(result)
        except Exception as e:
            return f"Error in power calculation: {str(e)}"

    @kernel_function(
        description="Calculate the square root of a number",
        name="square_root"
    )
    def square_root(self, a: float) -> str:
        """
        Calculate the square root of a number.

        Args:
            a: Number to calculate square root of

        Returns:
            Square root as a string
        """
        try:
            if a < 0:
                return "Error: Cannot calculate square root of negative number"
            result = a ** 0.5
            return str(result)
        except Exception as e:
            return f"Error in square root calculation: {str(e)}"

    @kernel_function(
        description="Calculate the percentage of a value",
        name="percentage"
    )
    def percentage(self, value: float, percent: float) -> str:
        """
        Calculate the percentage of a value.

        Args:
            value: The base value
            percent: The percentage to calculate

        Returns:
            Result as a string
        """
        try:
            result = (value * percent) / 100
            return str(result)
        except Exception as e:
            return f"Error in percentage calculation: {str(e)}"

    @kernel_function(
        description="Evaluate a simple mathematical expression",
        name="evaluate"
    )
    def evaluate(self, expression: str) -> str:
        """
        Evaluate a simple mathematical expression.

        Supports: +, -, *, /, **, %, parentheses

        Args:
            expression: Mathematical expression as a string

        Returns:
            Result as a string
        """
        try:
            # Only allow safe characters
            if not re.match(r'^[\d\s+\-*/%().]+$', expression):
                return "Error: Invalid characters in expression"

            # Evaluate in a safe manner with restricted builtins
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"

    @kernel_function(
        description="Convert celsius to fahrenheit",
        name="celsius_to_fahrenheit"
    )
    def celsius_to_fahrenheit(self, celsius: float) -> str:
        """
        Convert Celsius to Fahrenheit.

        Args:
            celsius: Temperature in Celsius

        Returns:
            Temperature in Fahrenheit as a string
        """
        try:
            result = (celsius * 9/5) + 32
            return f"{result:.2f}°F"
        except Exception as e:
            return f"Error in conversion: {str(e)}"

    @kernel_function(
        description="Convert fahrenheit to celsius",
        name="fahrenheit_to_celsius"
    )
    def fahrenheit_to_celsius(self, fahrenheit: float) -> str:
        """
        Convert Fahrenheit to Celsius.

        Args:
            fahrenheit: Temperature in Fahrenheit

        Returns:
            Temperature in Celsius as a string
        """
        try:
            result = (fahrenheit - 32) * 5/9
            return f"{result:.2f}°C"
        except Exception as e:
            return f"Error in conversion: {str(e)}"
