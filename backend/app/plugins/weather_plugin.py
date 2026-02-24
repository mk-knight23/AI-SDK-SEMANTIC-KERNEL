"""
Weather plugin for Semantic Kernel.

Provides weather information (mock implementation for demonstration).
"""

import random
from datetime import datetime
from typing import Optional

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from app.plugins.base import BasePlugin, PluginMetadata


class WeatherPlugin(BasePlugin):
    """
    Plugin for weather information.

    This is a mock implementation for demonstration purposes.
    In production, integrate with a real weather API.
    """

    # Mock weather data
    WEATHER_CONDITIONS = [
        "Sunny", "Partly Cloudy", "Cloudy", "Overcast",
        "Light Rain", "Heavy Rain", "Thunderstorm", "Snow",
        "Foggy", "Windy", "Clear"
    ]

    # Mock temperature ranges by city
    CITY_TEMPS = {
        "new york": (40, 85),
        "london": (35, 75),
        "tokyo": (45, 90),
        "paris": (38, 82),
        "sydney": (50, 95),
        "moscow": (20, 70),
        "dubai": (60, 110),
        "singapore": (75, 95),
        "mumbai": (70, 100),
        "san francisco": (50, 75),
    }

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="weather",
            description="Provides weather information (mock implementation)",
            version="1.0.0",
            author="AI-SDK-SEMANTIC-KERNEL"
        )

    @kernel_function(
        description="Get current weather for a city",
        name="current_weather"
    )
    def current_weather(self, city: str) -> str:
        """
        Get current weather for a city.

        Args:
            city: Name of the city

        Returns:
            Weather information as a string
        """
        city_lower = city.lower()

        # Get temperature range for city or use default
        temp_range = self.CITY_TEMPS.get(city_lower, (30, 90))
        temp = random.randint(*temp_range)

        # Get random condition
        condition = random.choice(self.WEATHER_CONDITIONS)

        # Generate humidity
        humidity = random.randint(30, 90)

        # Generate wind speed
        wind_speed = random.randint(0, 30)

        return (
            f"Current weather in {city.title()}:\n"
            f"  Temperature: {temp}°F\n"
            f"  Condition: {condition}\n"
            f"  Humidity: {humidity}%\n"
            f"  Wind: {wind_speed} mph"
        )

    @kernel_function(
        description="Get weather forecast for a city",
        name="weather_forecast"
    )
    def weather_forecast(self, city: str, days: int = 5) -> str:
        """
        Get weather forecast for a city.

        Args:
            city: Name of the city
            days: Number of days to forecast (1-7)

        Returns:
            Weather forecast as a string
        """
        city_lower = city.lower()
        days = min(max(days, 1), 7)  # Limit to 1-7 days

        temp_range = self.CITY_TEMPS.get(city_lower, (30, 90))

        forecast = f"{days}-Day Weather Forecast for {city.title()}:\n"

        for i in range(days):
            temp = random.randint(*temp_range)
            condition = random.choice(self.WEATHER_CONDITIONS)
            high = temp + random.randint(5, 15)
            low = temp - random.randint(5, 15)

            forecast += f"\n  Day {i + 1}: {condition}, High: {high}°F, Low: {low}°F"

        return forecast

    @kernel_function(
        description="Get temperature for a city",
        name="temperature"
    )
    def temperature(self, city: str) -> str:
        """
        Get current temperature for a city.

        Args:
            city: Name of the city

        Returns:
            Temperature as a string
        """
        city_lower = city.lower()
        temp_range = self.CITY_TEMPS.get(city_lower, (30, 90))
        temp = random.randint(*temp_range)

        # Also provide Celsius
        celsius = int((temp - 32) * 5 / 9)

        return f"Current temperature in {city.title()}: {temp}°F ({celsius}°C)"

    @kernel_function(
        description="Check if it will rain today",
        name="will_rain"
    )
    def will_rain(self, city: str) -> str:
        """
        Check if it will rain today in a city.

        Args:
            city: Name of the city

        Returns:
            Rain forecast as a string
        """
        rainy_conditions = ["Light Rain", "Heavy Rain", "Thunderstorm"]
        condition = random.choice(self.WEATHER_CONDITIONS)

        will_rain = condition in rainy_conditions
        rain_chance = random.randint(0, 100)

        if will_rain:
            return f"Yes, it is expected to rain in {city.title()} today. Chance of rain: {rain_chance}%"
        else:
            return f"No rain expected in {city.title()} today. Chance of rain: {rain_chance}%"

    @kernel_function(
        description="Get humidity level for a city",
        name="humidity"
    )
    def humidity(self, city: str) -> str:
        """
        Get current humidity level for a city.

        Args:
            city: Name of the city

        Returns:
            Humidity as a string
        """
        humidity = random.randint(30, 90)

        description = "Comfortable"
        if humidity > 80:
            description = "Very humid"
        elif humidity > 60:
            description = "Humid"
        elif humidity < 40:
            description = "Dry"

        return f"Current humidity in {city.title()}: {humidity}% ({description})"

    @kernel_function(
        description="Get UV index for a city",
        name="uv_index"
    )
    def uv_index(self, city: str) -> str:
        """
        Get UV index for a city.

        Args:
            city: Name of the city

        Returns:
            UV index as a string
        """
        uv = random.randint(0, 11)

        if uv <= 2:
            level = "Low"
            advice = "No protection needed"
        elif uv <= 5:
            level = "Moderate"
            advice = "Wear sunscreen"
        elif uv <= 7:
            level = "High"
            advice = "Wear sunscreen and protective clothing"
        elif uv <= 10:
            level = "Very High"
            advice = "Take extra precautions"
        else:
            level = "Extreme"
            advice = "Avoid sun exposure"

        return f"UV Index in {city.title()}: {uv} ({level}) - {advice}"
