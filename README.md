# UK Weather MCP Server

[![Test MCP Server](https://github.com/kaihendry/uk-weather-mcp-via-skill/actions/workflows/test-mcp.yml/badge.svg)](https://github.com/kaihendry/uk-weather-mcp-via-skill/actions/workflows/test-mcp.yml)

A Model Context Protocol (MCP) server that provides access to UK Met Office Weather DataHub API, enabling LLMs to fetch real-time weather forecasts for any global location.

## Features

- **Hourly Forecasts**: Detailed weather data for up to 48 hours ahead
- **3-Hourly Forecasts**: Medium-term forecasts for up to 7 days with 3-hour intervals
- **Daily Forecasts**: Daily summaries for up to 7 days ahead
- **Dual Output Formats**: Markdown for human readability, JSON for programmatic processing
- **Global Coverage**: Weather data for any location worldwide
- **Comprehensive Data**: Temperature, wind, precipitation, humidity, pressure, UV index, and more

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- UK Met Office DataHub API key (get one at https://datahub.metoffice.gov.uk/)

### Setup

1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone or download this repository and navigate to it:

```bash
cd uk-weather-mcp
```

3. Install dependencies:

```bash
uv sync
```

4. Set your Met Office API key as an environment variable:

```bash
export MET_OFFICE_API_KEY="your_api_key_here"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Run the Server

#### Development Mode

```bash
uv run uk_weather_mcp.py
```

#### With Environment Variables

```bash
MET_OFFICE_API_KEY="your_key" uv run uk_weather_mcp.py
```

### Claude Desktop Integration

To integrate with Claude Desktop, add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "uk-weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/uk-weather-mcp",
        "run",
        "uk_weather_mcp.py"
      ],
      "env": {
        "MET_OFFICE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Replace `/absolute/path/to/uk-weather-mcp` with the actual absolute path to this directory.

## Available Tools

### 1. `uk_weather_get_hourly_forecast`

Get detailed hourly weather forecasts for up to 48 hours ahead.

**Parameters:**
- `latitude` (float, required): Latitude in decimal degrees (-90 to 90)
- `longitude` (float, required): Longitude in decimal degrees (-180 to 180)
- `response_format` (string, optional): "markdown" (default) or "json"

**Example:**
```json
{
  "latitude": 51.5074,
  "longitude": -0.1278,
  "response_format": "markdown"
}
```

### 2. `uk_weather_get_three_hourly_forecast`

Get weather forecasts at 3-hour intervals for up to 7 days ahead.

**Parameters:**
- `latitude` (float, required): Latitude in decimal degrees (-90 to 90)
- `longitude` (float, required): Longitude in decimal degrees (-180 to 180)
- `response_format` (string, optional): "markdown" (default) or "json"

**Example:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "response_format": "json"
}
```

### 3. `uk_weather_get_daily_forecast`

Get daily weather summaries for up to 7 days ahead.

**Parameters:**
- `latitude` (float, required): Latitude in decimal degrees (-90 to 90)
- `longitude` (float, required): Longitude in decimal degrees (-180 to 180)
- `response_format` (string, optional): "markdown" (default) or "json"

**Example:**
```json
{
  "latitude": 48.8566,
  "longitude": 2.3522,
  "response_format": "markdown"
}
```

## Weather Data Included

Each forecast provides comprehensive weather information:

- **Temperature**: Actual and "feels like" temperature (°C)
- **Wind**: Speed (m/s) and direction (degrees)
- **Precipitation**: Total amount (mm)
- **Humidity**: Relative humidity (%)
- **Visibility**: Distance (meters)
- **Pressure**: Mean sea level pressure (Pa)
- **UV Index**: UV radiation intensity
- **Weather Conditions**: Significant weather codes

## Error Handling

The server provides clear, actionable error messages:

- **API Key Issues**: "Error: API key invalid or missing. Please check the MET_OFFICE_API_KEY environment variable"
- **Invalid Location**: "Error: Weather data not available for this location"
- **Rate Limits**: "Error: Rate limit exceeded. Please wait before making more requests"
- **Network Issues**: "Error: Request timed out" or "Error: Could not connect to Met Office API"

## Response Formats

### Markdown Format (Default)

Human-readable format with:
- Clear section headers
- Formatted timestamps (UTC)
- Organized weather parameters
- Limited to 20 forecast periods for readability

### JSON Format

Machine-readable GeoJSON format with:
- Complete forecast data
- All available weather parameters
- Full time series
- Metadata and geometry information

## Character Limits

Responses are automatically truncated if they exceed 25,000 characters, with a clear notice and guidance on how to get more specific data.

## Development

### Project Structure

```
uk-weather-mcp/
├── .github/
│   ├── workflows/
│   │   └── test-mcp.yml   # GitHub Actions CI/CD workflow
│   └── SETUP.md           # GitHub Actions setup guide
├── uk_weather_mcp.py      # Main MCP server implementation
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # This file
├── .env.example           # Example environment variables
├── test_examples.md       # Test scenarios and examples
└── CLAUDE.md              # Project instructions
```

### Testing

#### Local Testing

Run the server in development mode:

```bash
uv run uk_weather_mcp.py
```

The server will start and wait for MCP protocol messages over stdio.

#### Automated Testing with GitHub Actions

The repository includes a comprehensive GitHub Actions workflow that automatically tests:

- ✅ Python syntax validation
- ✅ Server initialization
- ✅ All three forecast tools (hourly, 3-hourly, daily)
- ✅ Both output formats (Markdown and JSON)
- ✅ Error handling for invalid inputs
- ✅ Multiple global locations

**Setup Instructions:**

1. Add your Met Office API key as a GitHub secret named `MET_OFFICE_API_KEY`
2. See [.github/SETUP.md](.github/SETUP.md) for detailed setup instructions
3. The workflow runs automatically on push and pull requests
4. Manual runs can be triggered from the Actions tab

The workflow uses `uv` for dependency management and runs on Ubuntu with Python 3.12.

### Code Quality

The server follows MCP best practices:

- **FastMCP Framework**: Uses the official Python MCP SDK
- **Pydantic Validation**: Robust input validation with clear error messages
- **Async/Await**: Efficient async HTTP requests
- **Code Reusability**: Shared utilities for API requests, error handling, and formatting
- **Tool Annotations**: Proper hints (readOnlyHint, idempotentHint, openWorldHint)
- **Comprehensive Documentation**: Detailed docstrings with usage examples

## License

MIT License - feel free to use and modify as needed.

## Credits

Weather data provided by the UK Met Office DataHub API.
