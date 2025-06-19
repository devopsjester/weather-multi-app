# Weather Multi-Interface Application

A comprehensive weather application with three interfaces (CLI, Web, and MCP Server) that provides current weather conditions and 3-day forecasts for locations worldwide.

## Features

- **Multiple Interfaces**: CLI, Web (Flask), and MCP Server for VS Code
- **Flexible Location Input**: 
  - US ZIP codes
  - City + State (US)
  - City + State/Province + Country (worldwide)
- **Smart Units**: Imperial units for US locations, metric elsewhere
- **Free APIs**: Uses keyless OpenWeatherMap and other free weather services
- **Robust Architecture**: Built with SOLID principles and Onion architecture
- **Comprehensive Testing**: Extensive unit tests including edge cases

## Architecture

The application follows Onion Architecture with clear separation of concerns:

```
├── src/
│   ├── domain/              # Core business logic (innermost layer)
│   ├── application/         # Application services and use cases
│   ├── infrastructure/      # External integrations (APIs, data access)
│   └── interfaces/          # User interfaces (CLI, Web, MCP)
```

## Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/devopsjester/weather-multi-app.git
cd weather-multi-app
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Try the Demo
```bash
python demo.py
```

### 3. Use Any Interface

**CLI:**
```bash
python -m weather_app cli weather --zipcode 90210
python -m weather_app cli weather --city "London" --country "UK"
```

**Web:**
```bash
python -m weather_app web
# Visit http://localhost:5000
```

**MCP Server:**
```bash
python -m weather_app mcp
# Configure in VS Code MCP settings or use .vscode/mcp.json
```

### VS Code Integration

This project includes MCP (Model Context Protocol) server integration for VS Code:

1. **Automatic Setup**: The `.vscode/mcp.json` file configures the weather MCP server
2. **Available Tools**:
   - `get_weather_by_zipcode` - Get weather by US zipcode
   - `get_weather_by_city` - Get weather by city/state/country  
   - `get_weather_summary` - Get human-readable weather summary
3. **Usage**: Ask GitHub Copilot Chat questions like "What's the weather in London using MCP?"

## Usage

### CLI Interface
```bash
# By ZIP code
python -m weather_app cli --zipcode 90210

# By city and state
python -m weather_app cli --city "Los Angeles" --state "CA"

# By city, state/province, and country
python -m weather_app cli --city "Toronto" --state "ON" --country "CA"
```

### Web Interface
```bash
# Start the Flask web server
python -m weather_app web

# Navigate to http://localhost:5000
```

### MCP Server (VS Code)
```bash
# Start the MCP server
python -m weather_app mcp

# Configure in VS Code MCP settings
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run tests with coverage
pytest --cov=weather_app --cov-report=html

# Run specific test file
pytest tests/test_domain_models.py -v
```

### Code Quality
```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black src/ tests/
isort src/ tests/

# Check code quality
flake8 src/ tests/
mypy src/
```

### Docker Deployment
```bash
# Build Docker image
docker build -t weather-multi-app .

# Run web interface in Docker
docker run -p 5000:5000 weather-multi-app

# Run CLI in Docker
docker run -it weather-multi-app python -m weather_app cli weather --city "London" --country "UK"
```

## Project Structure

```
weather-multi-app/
├── src/
│   ├── weather_app/
│   │   ├── domain/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── exceptions/
│   │   ├── application/
│   │   │   ├── services/
│   │   │   └── dtos/
│   │   ├── infrastructure/
│   │   │   ├── weather_apis/
│   │   │   └── location_services/
│   │   └── interfaces/
│   │       ├── cli/
│   │       ├── web/
│   │       └── mcp/
├── tests/
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
        └── ci-cd.yml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.
