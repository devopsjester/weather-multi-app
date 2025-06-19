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

## Installation

1. Clone the repository:
```bash
git clone https://github.com/devopsjester/weather-multi-app.git
cd weather-multi-app
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

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
pytest
```

### Code Formatting
```bash
black src/ tests/
isort src/ tests/
```

### Type Checking
```bash
mypy src/
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
