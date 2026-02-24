"""
Unit tests for Semantic Kernel plugins.
"""

import pytest
from app.plugins.time_plugin import TimePlugin
from app.plugins.calculator_plugin import CalculatorPlugin
from app.plugins.weather_plugin import WeatherPlugin
from app.plugins.text_plugin import TextPlugin
from app.plugins.base import PluginRegistry


class TestTimePlugin:
    """Test cases for TimePlugin."""

    def test_plugin_metadata(self):
        """Test plugin metadata."""
        metadata = TimePlugin.get_metadata()

        assert metadata.name == "time"
        assert metadata.description is not None
        assert metadata.version == "1.0.0"

    def test_current_time(self):
        """Test getting current time."""
        plugin = TimePlugin()
        result = plugin.current_time()

        assert "T" in result  # ISO format contains T

    def test_current_date(self):
        """Test getting current date."""
        plugin = TimePlugin()
        result = plugin.current_date()

        assert "-" in result  # YYYY-MM-DD format

    def test_parse_date(self):
        """Test parsing a date."""
        plugin = TimePlugin()
        result = plugin.parse_date("2024-01-15")

        assert "2024" in result

    def test_add_days(self):
        """Test adding days to a date."""
        plugin = TimePlugin()
        result = plugin.add_days("2024-01-01", 7)

        assert "2024-01-08" in result

    def test_day_of_week(self):
        """Test getting day of week."""
        plugin = TimePlugin()
        result = plugin.day_of_week("2024-01-01")  # Known Monday

        assert "Monday" in result


class TestCalculatorPlugin:
    """Test cases for CalculatorPlugin."""

    def test_plugin_metadata(self):
        """Test plugin metadata."""
        metadata = CalculatorPlugin.get_metadata()

        assert metadata.name == "calculator"
        assert metadata.description is not None

    def test_add(self):
        """Test addition."""
        plugin = CalculatorPlugin()
        result = plugin.add(5, 3)

        assert result == "8"

    def test_subtract(self):
        """Test subtraction."""
        plugin = CalculatorPlugin()
        result = plugin.subtract(10, 4)

        assert result == "6"

    def test_multiply(self):
        """Test multiplication."""
        plugin = CalculatorPlugin()
        result = plugin.multiply(6, 7)

        assert result == "42"

    def test_divide(self):
        """Test division."""
        plugin = CalculatorPlugin()
        result = plugin.divide(20, 4)

        assert result == "5"

    def test_divide_by_zero(self):
        """Test division by zero."""
        plugin = CalculatorPlugin()
        result = plugin.divide(10, 0)

        assert "Error" in result

    def test_power(self):
        """Test power operation."""
        plugin = CalculatorPlugin()
        result = plugin.power(2, 8)

        assert result == "256"

    def test_square_root(self):
        """Test square root."""
        plugin = CalculatorPlugin()
        result = plugin.square_root(144)

        assert result == "12"

    def test_percentage(self):
        """Test percentage calculation."""
        plugin = CalculatorPlugin()
        result = plugin.percentage(200, 25)

        assert result == "50"


class TestWeatherPlugin:
    """Test cases for WeatherPlugin."""

    def test_plugin_metadata(self):
        """Test plugin metadata."""
        metadata = WeatherPlugin.get_metadata()

        assert metadata.name == "weather"
        assert "mock" in metadata.description.lower()

    def test_current_weather(self):
        """Test getting current weather."""
        plugin = WeatherPlugin()
        result = plugin.current_weather("Tokyo")

        assert "Tokyo" in result
        assert "Temperature" in result

    def test_weather_forecast(self):
        """Test weather forecast."""
        plugin = WeatherPlugin()
        result = plugin.weather_forecast("London", days=3)

        assert "London" in result
        assert "Day" in result

    def test_temperature(self):
        """Test getting temperature."""
        plugin = WeatherPlugin()
        result = plugin.temperature("Paris")

        assert "Paris" in result
        assert "°F" in result
        assert "°C" in result


class TestTextPlugin:
    """Test cases for TextPlugin."""

    def test_plugin_metadata(self):
        """Test plugin metadata."""
        metadata = TextPlugin.get_metadata()

        assert metadata.name == "text"
        assert metadata.description is not None

    def test_to_upper(self):
        """Test converting to uppercase."""
        plugin = TextPlugin()
        result = plugin.to_upper("hello world")

        assert result == "HELLO WORLD"

    def test_to_lower(self):
        """Test converting to lowercase."""
        plugin = TextPlugin()
        result = plugin.to_lower("HELLO WORLD")

        assert result == "hello world"

    def test_capitalize(self):
        """Test capitalizing."""
        plugin = TextPlugin()
        result = plugin.capitalize("hello world")

        assert result == "Hello World"

    def test_reverse(self):
        """Test reversing text."""
        plugin = TextPlugin()
        result = plugin.reverse("hello")

        assert result == "olleh"

    def test_word_count(self):
        """Test word count."""
        plugin = TextPlugin()
        result = plugin.word_count("hello world test")

        assert result == "3"

    def test_char_count(self):
        """Test character count."""
        plugin = TextPlugin()
        result = plugin.char_count("test")

        assert result == "4"

    def test_extract_emails(self):
        """Test email extraction."""
        plugin = TextPlugin()
        text = "Contact us at test@example.com or support@test.org"
        result = plugin.extract_emails(text)

        assert "test@example.com" in result
        assert "support@test.org" in result

    def test_extract_urls(self):
        """Test URL extraction."""
        plugin = TextPlugin()
        text = "Visit https://example.com or http://test.org"
        result = plugin.extract_urls(text)

        assert "https://example.com" in result
        assert "http://test.org" in result

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        plugin = TextPlugin()
        result = plugin.normalize_whitespace("hello    world   test")

        assert result == "hello world test"

    def test_truncate(self):
        """Test text truncation."""
        plugin = TextPlugin()
        result = plugin.truncate("hello world", 5)

        assert len(result) == 8  # "hello..." = 8 chars with ellipsis


class TestPluginRegistry:
    """Test cases for PluginRegistry."""

    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        plugin = TimePlugin()

        registry.register(plugin)

        assert len(registry.list_plugins()) == 1
        assert registry.get_plugin("time") is not None

    def test_register_duplicate_raises_error(self):
        """Test that registering duplicate raises error."""
        registry = PluginRegistry()
        plugin1 = TimePlugin()
        plugin2 = TimePlugin()

        registry.register(plugin1)

        with pytest.raises(ValueError):
            registry.register(plugin2)

    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        plugin = TimePlugin()

        registry.register(plugin)
        assert len(registry.list_plugins()) == 1

        registry.unregister("time")
        assert len(registry.list_plugins()) == 0

    def test_get_all_metadata(self):
        """Test getting all plugin metadata."""
        registry = PluginRegistry()
        registry.register(TimePlugin())
        registry.register(CalculatorPlugin())

        metadata = registry.get_all_metadata()

        assert "time" in metadata
        assert "calculator" in metadata
