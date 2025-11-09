#!/usr/bin/env python3
"""
MCP Server for UK Met Office Weather DataHub API.

This server provides tools to fetch weather forecasts from the UK Met Office DataHub,
including hourly, 3-hourly, and daily forecasts for any global location.
"""

import os
import json
from typing import Dict, Any
from enum import Enum
from datetime import datetime
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("uk_weather_mcp")

# Constants
API_BASE_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point"
CHARACTER_LIMIT = 25000  # Maximum response size in characters
DEFAULT_TIMEOUT = 30.0  # Seconds

# Get API key from environment
API_KEY = os.getenv("MET_OFFICE_API_KEY", "")

# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# Pydantic Models for Input Validation
class WeatherForecastInput(BaseModel):
    """Input model for weather forecast operations."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    latitude: float = Field(
        ...,
        description="Latitude in decimal degrees (e.g., 51.5074 for London, 40.7128 for New York)",
        ge=-90.0,
        le=90.0
    )
    longitude: float = Field(
        ...,
        description="Longitude in decimal degrees (e.g., -0.1278 for London, -74.0060 for New York)",
        ge=-180.0,
        le=180.0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not -90.0 <= v <= 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not -180.0 <= v <= 180.0:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v


# Shared utility functions
async def _make_api_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reusable function for all Met Office API calls.

    Args:
        endpoint: API endpoint path (e.g., "hourly", "daily")
        params: Query parameters (latitude, longitude)

    Returns:
        dict: Parsed JSON response from the API

    Raises:
        httpx.HTTPStatusError: For HTTP error responses
        httpx.TimeoutException: For request timeouts
    """
    if not API_KEY:
        raise ValueError("MET_OFFICE_API_KEY environment variable is not set")

    url = f"{API_BASE_URL}/{endpoint}"
    headers = {
        "accept": "application/json",
        "apikey": API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params=params,
            headers=headers,
            timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """
    Consistent error formatting across all tools.

    Converts technical exceptions into clear, actionable error messages
    that guide users toward resolution.

    Args:
        e: Exception caught during API request

    Returns:
        str: User-friendly error message with suggested actions
    """
    if isinstance(e, ValueError):
        return f"Error: {str(e)}"
    elif isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 401:
            return "Error: API key invalid or missing. Please check the MET_OFFICE_API_KEY environment variable is set correctly."
        elif status == 404:
            return "Error: Weather data not available for this location. The coordinates may be invalid or outside the service area."
        elif status == 429:
            return "Error: Rate limit exceeded. Please wait a few moments before making more requests."
        elif status == 400:
            return "Error: Invalid request parameters. Please check that latitude and longitude are valid decimal degrees."
        return f"Error: API request failed with status {status}. Please try again later."
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The Met Office API may be experiencing issues. Please try again."
    elif isinstance(e, httpx.ConnectError):
        return "Error: Could not connect to Met Office API. Please check your internet connection."
    return f"Error: Unexpected error occurred: {type(e).__name__}. Please try again."


def _format_timestamp(timestamp_str: str) -> str:
    """
    Convert ISO 8601 timestamp to human-readable format.

    Args:
        timestamp_str: ISO 8601 timestamp string

    Returns:
        str: Human-readable timestamp (e.g., "2024-01-15 14:00 UTC")
    """
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return timestamp_str


def _format_weather_markdown(data: Dict[str, Any], forecast_type: str) -> str:
    """
    Format weather forecast data as Markdown for human readability.

    Args:
        data: Weather forecast data from API
        forecast_type: Type of forecast (hourly, 3-hourly, daily)

    Returns:
        str: Markdown-formatted weather forecast
    """
    lines = []

    # Header
    features = data.get("features", [])
    if not features:
        return "No weather data available."

    feature = features[0]
    geometry = feature.get("geometry", {})
    coords = geometry.get("coordinates", [])

    if len(coords) >= 2:
        lon, lat = coords[0], coords[1]
        lines.append(f"# Weather Forecast ({forecast_type})")
        lines.append(f"**Location:** {lat:.4f}°N, {lon:.4f}°E")
        lines.append("")

    # Time series data
    properties = feature.get("properties", {})
    time_series = properties.get("timeSeries", [])

    if not time_series:
        return "No forecast data available."

    lines.append(f"**Forecast periods:** {len(time_series)}")
    lines.append("")

    # Display forecast entries
    for i, entry in enumerate(time_series[:20]):  # Limit to first 20 entries
        time = entry.get("time", "Unknown time")
        formatted_time = _format_timestamp(time)

        lines.append(f"## {formatted_time}")

        # Screen temperature
        if "screenTemperature" in entry:
            temp = entry["screenTemperature"]
            lines.append(f"- **Temperature:** {temp}°C")

        # Feels like temperature
        if "feelsLikeTemperature" in entry:
            feels = entry["feelsLikeTemperature"]
            lines.append(f"- **Feels Like:** {feels}°C")

        # Wind
        if "windSpeed10m" in entry:
            wind_speed = entry["windSpeed10m"]
            wind_dir = entry.get("windDirectionFrom10m", "N/A")
            lines.append(f"- **Wind:** {wind_speed} m/s from {wind_dir}°")

        # Precipitation
        if "totalPrecipAmount" in entry:
            precip = entry["totalPrecipAmount"]
            lines.append(f"- **Precipitation:** {precip} mm")

        # Humidity
        if "screenRelativeHumidity" in entry:
            humidity = entry["screenRelativeHumidity"]
            lines.append(f"- **Humidity:** {humidity}%")

        # Visibility
        if "visibility" in entry:
            visibility = entry["visibility"]
            lines.append(f"- **Visibility:** {visibility} m")

        # Pressure
        if "mslp" in entry:
            pressure = entry["mslp"]
            lines.append(f"- **Pressure:** {pressure} Pa")

        # UV Index
        if "uvIndex" in entry:
            uv = entry["uvIndex"]
            lines.append(f"- **UV Index:** {uv}")

        # Weather description
        if "significantWeatherCode" in entry:
            weather_code = entry["significantWeatherCode"]
            lines.append(f"- **Weather Code:** {weather_code}")

        lines.append("")

    # Add truncation notice if needed
    if len(time_series) > 20:
        lines.append(f"*Showing first 20 of {len(time_series)} forecast periods. Use JSON format for complete data.*")

    return "\n".join(lines)


def _truncate_if_needed(content: str, data: Dict[str, Any], is_json: bool = False) -> str:
    """
    Check response size and truncate if it exceeds CHARACTER_LIMIT.

    Args:
        content: Formatted response string
        data: Original data for truncation reference
        is_json: Whether the content is JSON format

    Returns:
        str: Original or truncated content with truncation notice
    """
    if len(content) <= CHARACTER_LIMIT:
        return content

    # For JSON, truncate features array to keep it valid JSON
    if is_json:
        import json
        try:
            parsed = json.loads(content)
            if "features" in parsed and len(parsed["features"]) > 0:
                # Reduce time series data
                feature = parsed["features"][0]
                if "properties" in feature and "timeSeries" in feature["properties"]:
                    time_series = feature["properties"]["timeSeries"]
                    # Keep reducing until under limit
                    for keep_count in [20, 10, 5, 1]:
                        feature["properties"]["timeSeries"] = time_series[:keep_count]
                        truncated_json = json.dumps(parsed, indent=2)
                        if len(truncated_json) <= CHARACTER_LIMIT:
                            return truncated_json
                    # If still too big, return minimal structure
                    return json.dumps({
                        "error": "Response too large",
                        "message": f"Forecast data exceeds {CHARACTER_LIMIT} character limit. Try requesting a shorter time period."
                    }, indent=2)
        except json.JSONDecodeError:
            pass

    # For Markdown, just truncate and add notice
    truncated = content[:CHARACTER_LIMIT]
    truncated += "\n\n---\n\n"
    truncated += f"**Response truncated** (exceeded {CHARACTER_LIMIT} character limit). "
    truncated += "Try using JSON format with filtering or requesting a shorter forecast period."

    return truncated


# Tool definitions
@mcp.tool(
    name="uk_weather_get_hourly_forecast",
    annotations={
        "title": "Get Hourly Weather Forecast",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def uk_weather_get_hourly_forecast(params: WeatherForecastInput) -> str:
    """
    Get hourly weather forecast for a specific location from the UK Met Office.

    This tool fetches detailed hourly weather forecasts for up to 48 hours ahead
    for any global location. It provides comprehensive weather parameters including
    temperature, wind, precipitation, humidity, pressure, and more.

    Args:
        params (WeatherForecastInput): Validated input parameters containing:
            - latitude (float): Latitude in decimal degrees, -90 to 90 (e.g., 51.5074 for London)
            - longitude (float): Longitude in decimal degrees, -180 to 180 (e.g., -0.1278 for London)
            - response_format (ResponseFormat): 'markdown' (default, human-readable) or 'json' (machine-readable)

    Returns:
        str: Weather forecast data in the requested format

        Markdown format includes:
        - Location coordinates
        - Forecast period information
        - For each hour: time, temperature, feels-like temperature, wind, precipitation,
          humidity, visibility, pressure, UV index, and weather conditions
        - Limited to first 20 hours for readability (use JSON for complete data)

        JSON format includes:
        - Complete GeoJSON response with all available weather parameters
        - Full 48-hour forecast
        - All metadata and geometry information

        Error format:
        - "Error: <specific error message with resolution guidance>"

    Examples:
        - Use when: "What's the weather forecast for London today?"
          → params with latitude=51.5074, longitude=-0.1278

        - Use when: "Give me hourly weather for New York for the next 48 hours"
          → params with latitude=40.7128, longitude=-74.0060

        - Don't use when: Need weekly forecast (use uk_weather_get_daily_forecast instead)

        - Don't use when: Need 3-hourly intervals (use uk_weather_get_three_hourly_forecast instead)

    Error Handling:
        - Returns "Error: MET_OFFICE_API_KEY environment variable is not set" if API key missing
        - Returns "Error: API key invalid or missing" if authentication fails (401)
        - Returns "Error: Weather data not available for this location" if coordinates invalid (404)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Returns "Error: Request timed out" if API is slow or unavailable
        - Input validation errors handled automatically by Pydantic model
    """
    try:
        # Make API request using validated parameters
        data = await _make_api_request(
            "hourly",
            {
                "latitude": params.latitude,
                "longitude": params.longitude
            }
        )

        # Format response based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_weather_markdown(data, "Hourly")
            return _truncate_if_needed(result, data, is_json=False)
        else:
            # Machine-readable JSON format
            result = json.dumps(data, indent=2)
            return _truncate_if_needed(result, data, is_json=True)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="uk_weather_get_three_hourly_forecast",
    annotations={
        "title": "Get 3-Hourly Weather Forecast",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def uk_weather_get_three_hourly_forecast(params: WeatherForecastInput) -> str:
    """
    Get 3-hourly weather forecast for a specific location from the UK Met Office.

    This tool fetches weather forecasts at 3-hour intervals for up to 168 hours (7 days)
    ahead for any global location. Ideal for medium-term planning where hourly detail
    is not required.

    Args:
        params (WeatherForecastInput): Validated input parameters containing:
            - latitude (float): Latitude in decimal degrees, -90 to 90 (e.g., 51.5074 for London)
            - longitude (float): Longitude in decimal degrees, -180 to 180 (e.g., -0.1278 for London)
            - response_format (ResponseFormat): 'markdown' (default, human-readable) or 'json' (machine-readable)

    Returns:
        str: Weather forecast data in the requested format

        Markdown format includes:
        - Location coordinates
        - Forecast period information
        - For each 3-hour period: time, temperature, feels-like temperature, wind,
          precipitation, humidity, visibility, pressure, UV index, weather conditions
        - Limited to first 20 periods for readability (use JSON for complete data)

        JSON format includes:
        - Complete GeoJSON response with all available weather parameters
        - Full 7-day forecast at 3-hour intervals
        - All metadata and geometry information

        Error format:
        - "Error: <specific error message with resolution guidance>"

    Examples:
        - Use when: "What's the weather forecast for this week in Edinburgh?"
          → params with latitude=55.9533, longitude=-3.1883

        - Use when: "Give me a 7-day forecast for Paris every 3 hours"
          → params with latitude=48.8566, longitude=2.3522

        - Don't use when: Need hourly detail for next 48 hours (use uk_weather_get_hourly_forecast)

        - Don't use when: Need daily summary (use uk_weather_get_daily_forecast instead)

    Error Handling:
        - Returns "Error: MET_OFFICE_API_KEY environment variable is not set" if API key missing
        - Returns "Error: API key invalid or missing" if authentication fails (401)
        - Returns "Error: Weather data not available for this location" if coordinates invalid (404)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Returns "Error: Request timed out" if API is slow or unavailable
        - Input validation errors handled automatically by Pydantic model
    """
    try:
        # Make API request using validated parameters
        data = await _make_api_request(
            "three-hourly",
            {
                "latitude": params.latitude,
                "longitude": params.longitude
            }
        )

        # Format response based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_weather_markdown(data, "3-Hourly")
            return _truncate_if_needed(result, data, is_json=False)
        else:
            # Machine-readable JSON format
            result = json.dumps(data, indent=2)
            return _truncate_if_needed(result, data, is_json=True)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="uk_weather_get_daily_forecast",
    annotations={
        "title": "Get Daily Weather Forecast",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def uk_weather_get_daily_forecast(params: WeatherForecastInput) -> str:
    """
    Get daily weather forecast summary for a specific location from the UK Met Office.

    This tool fetches daily weather summaries for up to 168 hours (7 days) ahead
    for any global location. Provides high-level daily conditions ideal for long-term
    planning and travel.

    Args:
        params (WeatherForecastInput): Validated input parameters containing:
            - latitude (float): Latitude in decimal degrees, -90 to 90 (e.g., 51.5074 for London)
            - longitude (float): Longitude in decimal degrees, -180 to 180 (e.g., -0.1278 for London)
            - response_format (ResponseFormat): 'markdown' (default, human-readable) or 'json' (machine-readable)

    Returns:
        str: Weather forecast data in the requested format

        Markdown format includes:
        - Location coordinates
        - Forecast period information
        - For each day: date, daily temperature range, wind conditions, precipitation totals,
          humidity levels, visibility, pressure, UV index, overall weather conditions
        - All daily periods shown (typically 7 days)

        JSON format includes:
        - Complete GeoJSON response with all available daily weather parameters
        - Full 7-day daily forecast
        - All metadata and geometry information

        Error format:
        - "Error: <specific error message with resolution guidance>"

    Examples:
        - Use when: "What's the weather going to be like in Manchester next week?"
          → params with latitude=53.4808, longitude=-2.2426

        - Use when: "Give me a weekly forecast for Dublin"
          → params with latitude=53.3498, longitude=-6.2603

        - Don't use when: Need hourly details (use uk_weather_get_hourly_forecast)

        - Don't use when: Need 3-hour intervals (use uk_weather_get_three_hourly_forecast)

    Error Handling:
        - Returns "Error: MET_OFFICE_API_KEY environment variable is not set" if API key missing
        - Returns "Error: API key invalid or missing" if authentication fails (401)
        - Returns "Error: Weather data not available for this location" if coordinates invalid (404)
        - Returns "Error: Rate limit exceeded" if too many requests (429)
        - Returns "Error: Request timed out" if API is slow or unavailable
        - Input validation errors handled automatically by Pydantic model
    """
    try:
        # Make API request using validated parameters
        data = await _make_api_request(
            "daily",
            {
                "latitude": params.latitude,
                "longitude": params.longitude
            }
        )

        # Format response based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_weather_markdown(data, "Daily")
            return _truncate_if_needed(result, data, is_json=False)
        else:
            # Machine-readable JSON format
            result = json.dumps(data, indent=2)
            return _truncate_if_needed(result, data, is_json=True)

    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
