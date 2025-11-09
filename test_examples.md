# UK Weather MCP Server - Test Examples

This document provides example questions and usage scenarios for testing the UK Weather MCP server. Due to the real-time nature of weather data, these are example queries rather than evaluation questions with stable answers.

## Example Queries

### Example 1: Simple Location Forecast

**Query**: "What's the weather forecast for London today?"

**Expected Tool Call**: `uk_weather_get_hourly_forecast`
```json
{
  "latitude": 51.5074,
  "longitude": -0.1278,
  "response_format": "markdown"
}
```

**Expected Result**: Hourly forecast for London showing temperature, wind, precipitation, humidity, etc.

---

### Example 2: Multi-Day Forecast

**Query**: "Give me the week-ahead forecast for Edinburgh."

**Expected Tool Call**: `uk_weather_get_daily_forecast`
```json
{
  "latitude": 55.9533,
  "longitude": -3.1883,
  "response_format": "markdown"
}
```

**Expected Result**: 7-day daily forecast for Edinburgh.

---

### Example 3: Specific Time Intervals

**Query**: "I need 3-hourly weather updates for Manchester for the next week."

**Expected Tool Call**: `uk_weather_get_three_hourly_forecast`
```json
{
  "latitude": 53.4808,
  "longitude": -2.2426,
  "response_format": "markdown"
}
```

**Expected Result**: 7-day forecast at 3-hour intervals for Manchester.

---

### Example 4: JSON Format for Processing

**Query**: "Get me the hourly weather data for Dublin in JSON format so I can analyze it."

**Expected Tool Call**: `uk_weather_get_hourly_forecast`
```json
{
  "latitude": 53.3498,
  "longitude": -6.2603,
  "response_format": "json"
}
```

**Expected Result**: Complete GeoJSON response with all weather data.

---

### Example 5: International Location

**Query**: "What's the weather forecast for Tokyo for the next 48 hours?"

**Expected Tool Call**: `uk_weather_get_hourly_forecast`
```json
{
  "latitude": 35.6762,
  "longitude": 139.6503,
  "response_format": "markdown"
}
```

**Expected Result**: Hourly forecast for Tokyo.

---

### Example 6: Coordinates from User

**Query**: "Get the weather for coordinates 40.7128°N, 74.0060°W (New York)"

**Expected Tool Call**: `uk_weather_get_hourly_forecast`
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "response_format": "markdown"
}
```

**Expected Result**: Hourly forecast for New York City.

---

## Error Handling Tests

### Test 1: Invalid Coordinates (Out of Range)

**Query**: "Get weather for latitude 100, longitude 200"

**Expected Error**: "Error: Latitude must be between -90 and 90 degrees" or "Longitude must be between -180 and 180 degrees"

---

### Test 2: Missing API Key

**Query**: (Run without MET_OFFICE_API_KEY set) "Get London weather"

**Expected Error**: "Error: API key invalid or missing. Please check the MET_OFFICE_API_KEY environment variable is set correctly."

---

### Test 3: Invalid API Key

**Query**: (Run with incorrect API key) "Get London weather"

**Expected Error**: "Error: API key invalid or missing. Please check the MET_OFFICE_API_KEY environment variable is set correctly."

---

## Multi-Step Workflows

### Workflow 1: Travel Planning

**User Story**: "I'm planning a trip from London to Edinburgh next week. Help me understand the weather."

**Expected Tool Calls**:
1. `uk_weather_get_daily_forecast` for London
2. `uk_weather_get_daily_forecast` for Edinburgh
3. Compare conditions between the two locations

---

### Workflow 2: Event Planning

**User Story**: "I'm organizing an outdoor event in Manchester on Saturday. What's the hourly forecast?"

**Expected Tool Calls**:
1. `uk_weather_get_hourly_forecast` for Manchester
2. Examine Saturday's hourly conditions
3. Assess suitability for outdoor event

---

### Workflow 3: Detailed Analysis

**User Story**: "I need detailed weather data for Cardiff for analysis. Get me the 3-hourly data in JSON."

**Expected Tool Calls**:
1. `uk_weather_get_three_hourly_forecast` with `response_format: "json"`
2. Return complete GeoJSON for programmatic processing

---

## Tool Capability Tests

### Test 1: All Three Forecast Types

**Scenario**: Request all three forecast types for the same location to verify tool diversity.

**Calls**:
```json
// Hourly
{"latitude": 51.5074, "longitude": -0.1278, "response_format": "markdown"}

// 3-Hourly
{"latitude": 51.5074, "longitude": -0.1278, "response_format": "markdown"}

// Daily
{"latitude": 51.5074, "longitude": -0.1278, "response_format": "markdown"}
```

**Verification**: Each tool returns appropriate time intervals and format.

---

### Test 2: Both Response Formats

**Scenario**: Request same location in both markdown and JSON formats.

**Calls**:
```json
// Markdown
{"latitude": 51.5074, "longitude": -0.1278, "response_format": "markdown"}

// JSON
{"latitude": 51.5074, "longitude": -0.1278, "response_format": "json"}
```

**Verification**: Markdown is human-readable with formatting; JSON is valid GeoJSON.

---

## Major UK Cities Coordinates

For testing purposes, here are coordinates for major UK cities:

| City | Latitude | Longitude |
|------|----------|-----------|
| London | 51.5074 | -0.1278 |
| Edinburgh | 55.9533 | -3.1883 |
| Manchester | 53.4808 | -2.2426 |
| Cardiff | 51.4816 | -3.1791 |
| Birmingham | 52.4862 | -1.8904 |
| Glasgow | 55.8642 | -4.2518 |
| Liverpool | 53.4084 | -2.9916 |
| Bristol | 51.4545 | -2.5879 |
| Belfast | 54.5973 | -5.9301 |
| Newcastle | 54.9783 | -1.6178 |

---

## Expected Tool Behavior

### Tool: `uk_weather_get_hourly_forecast`
- **Time Range**: Up to 48 hours ahead
- **Interval**: Hourly
- **Data Includes**: Temperature, feels-like, wind, precipitation, humidity, visibility, pressure, UV index, weather codes
- **Markdown Limit**: First 20 hours displayed
- **JSON**: Complete 48-hour forecast

### Tool: `uk_weather_get_three_hourly_forecast`
- **Time Range**: Up to 168 hours (7 days) ahead
- **Interval**: 3-hourly
- **Data Includes**: Same as hourly
- **Markdown Limit**: First 20 periods displayed
- **JSON**: Complete 7-day forecast

### Tool: `uk_weather_get_daily_forecast`
- **Time Range**: Up to 168 hours (7 days) ahead
- **Interval**: Daily
- **Data Includes**: Daily summaries with temperature ranges, conditions
- **Markdown**: All days displayed
- **JSON**: Complete 7-day forecast

---

## Note on Evaluation

Traditional MCP server evaluations require questions with **stable, verifiable answers**. Since weather forecasts are inherently dynamic and change constantly, this server is better tested through:

1. **Functional testing**: Verify tools return valid responses
2. **Format testing**: Verify both markdown and JSON outputs are correct
3. **Error testing**: Verify proper error handling
4. **Usability testing**: Verify LLMs can effectively use tools for real queries
5. **Integration testing**: Verify tools work with Claude Desktop or other MCP clients
