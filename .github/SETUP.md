# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions for testing the UK Weather MCP server.

## Setting Up the MET_OFFICE_API_KEY Secret

The workflow requires your Met Office API key to be stored as a GitHub secret.

### Steps to Add the Secret

1. **Navigate to your repository on GitHub**

2. **Go to Settings**
   - Click on the "Settings" tab at the top of your repository

3. **Access Secrets**
   - In the left sidebar, click on "Secrets and variables"
   - Then click on "Actions"

4. **Add New Secret**
   - Click the "New repository secret" button
   - Name: `MET_OFFICE_API_KEY`
   - Value: Paste your Met Office API key (get one from https://datahub.metoffice.gov.uk/)
   - Click "Add secret"

### Verify the Secret

After adding the secret:

1. Go to the "Actions" tab in your repository
2. You should see the "Test MCP Server" workflow
3. Click "Run workflow" to manually trigger a test
4. The workflow should run successfully if the secret is set correctly

## What the Workflow Tests

The GitHub Actions workflow (`test-mcp.yml`) runs the following tests:

### 1. **Python Syntax Validation**
   - Verifies the Python code compiles without syntax errors

### 2. **Type Checking** (optional)
   - Runs mypy for type checking (doesn't fail the build)

### 3. **Server Initialization**
   - Tests that the MCP server can start without errors

### 4. **Tool Functionality**
   - Tests all three forecast tools:
     - `uk_weather_get_hourly_forecast`
     - `uk_weather_get_three_hourly_forecast`
     - `uk_weather_get_daily_forecast`
   - Tests both Markdown and JSON output formats
   - Uses London coordinates (51.5074, -0.1278) as test location

### 5. **Error Handling**
   - Tests invalid latitude (out of range)
   - Tests invalid longitude (out of range)
   - Tests missing API key handling

### 6. **Global Location Testing**
   - Tests forecasts for multiple locations worldwide:
     - London, UK
     - New York, USA
     - Tokyo, Japan
     - Sydney, Australia
     - Reykjavik, Iceland

### 7. **Test Report Generation**
   - Generates a summary in the GitHub Actions UI

## Workflow Triggers

The workflow runs automatically on:

- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop` branches
- **Manual trigger** via the Actions tab (workflow_dispatch)

## Viewing Test Results

1. Go to the "Actions" tab in your repository
2. Click on a workflow run to see details
3. Expand each step to see the output
4. Check the "Generate test report" step for a summary

## Troubleshooting

### Workflow Fails with "API key invalid"

**Solution**: Verify that:
- The secret name is exactly `MET_OFFICE_API_KEY` (case-sensitive)
- The API key is valid and active
- You have sufficient quota on your Met Office API account

### Workflow Fails on Tool Functionality Tests

**Solution**:
- Check if the Met Office API is accessible from GitHub Actions runners
- Verify your API key has permissions for the site-specific forecast endpoints
- Check the Met Office API status page for any service disruptions

### Syntax or Import Errors

**Solution**:
- Ensure all dependencies are listed in `pyproject.toml`
- Run `uv sync` locally to verify dependencies install correctly
- Check that Python version matches (3.12 in workflow, 3.10+ required)

## Local Testing

Before pushing, you can test locally:

```bash
# 1. Set your API key
export MET_OFFICE_API_KEY="your_key_here"

# 2. Install dependencies
uv sync

# 3. Check syntax
uv run python -m py_compile uk_weather_mcp.py

# 4. Test the server starts
timeout 5s uv run uk_weather_mcp.py

# 5. Run custom tests (create test scripts as shown in workflow)
```

## Cost Considerations

- GitHub Actions provides free minutes for public repositories
- The workflow typically takes 2-5 minutes to complete
- Each test makes real API calls to the Met Office API
- Consider your Met Office API quota limits

## Security Best Practices

✅ **Do:**
- Store API keys as GitHub secrets
- Use secrets for sensitive data
- Review the workflow before running

❌ **Don't:**
- Commit API keys to the repository
- Log API keys in workflow output
- Share secrets publicly

## Updating the Workflow

To modify the workflow:

1. Edit `.github/workflows/test-mcp.yml`
2. Test changes in a feature branch
3. Create a pull request to merge to main
4. Verify tests pass before merging

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Met Office DataHub](https://datahub.metoffice.gov.uk/)
- [uv Documentation](https://docs.astral.sh/uv/)
