# Baity Telegram Bot

A professional webhook service for posting real estate listings to city-specific Telegram channels.

## Features

- Receive webhooks from Baity backend when real estates are approved
- Post listings to city-specific Telegram channels
- Support for photos and formatted messages
- Batch and async processing options
- Rate limiting and retry logic
- Health checks for monitoring
- Docker support for easy deployment

## Project Structure

```
baity-telegram-bot/
├── app/
│   ├── api/                 # API layer
│   │   ├── deps.py         # Dependency injection
│   │   └── v1/
│   │       ├── router.py   # API router
│   │       └── endpoints/  # Endpoint handlers
│   ├── core/               # Core configuration
│   │   ├── config.py      # Settings
│   │   ├── logging.py     # Logging setup
│   │   └── exceptions.py  # Custom exceptions
│   ├── middleware/         # Middleware
│   │   ├── logging.py     # Request logging
│   │   └── error_handler.py
│   ├── schemas/            # Pydantic models
│   │   ├── realestate.py  # Request DTOs
│   │   └── response.py    # Response DTOs
│   ├── services/           # Business logic
│   │   ├── telegram.py    # Telegram service
│   │   └── message_formatter.py
│   └── main.py            # Application entry
├── tests/                  # Test suite
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Container orchestration
└── .env.example          # Environment template
```

## Quick Start

### Prerequisites

- Python 3.12+
- Telegram Bot Token (from @BotFather)
- Telegram channels for each city

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/baity-telegram-bot.git
cd baity-telegram-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram bot token | Yes | - |
| `WEBHOOK_API_KEY` | API key for webhook auth | Yes | - |
| `CITY_CHANNELS` | JSON mapping of city IDs to channels | No | See .env.example |
| `ENVIRONMENT` | Environment name | No | development |
| `DEBUG` | Enable debug mode | No | false |
| `LOG_LEVEL` | Logging level | No | INFO |

### City Channels

Configure city-to-channel mapping in `.env`:

```bash
CITY_CHANNELS={"1": "@baghdad_realestate", "2": "@basra_realestate"}
```

## API Endpoints

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/webhook/realestate` | Post single real estate |
| POST | `/api/v1/webhook/realestate/async` | Async posting |
| POST | `/api/v1/webhook/realestate/batch` | Batch posting |

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Full health check |
| GET | `/api/v1/health/ready` | Readiness probe |
| GET | `/api/v1/health/live` | Liveness probe |

### Authentication

All webhook endpoints require the `X-Api-Key` header:

```bash
curl -X POST https://your-server/api/v1/webhook/realestate \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{"id": "abc123", ...}'
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# With coverage
pytest --cov=app
```

### Code Quality

```bash
# Lint
ruff check app tests

# Type check
mypy app
```

## Extending the Bot

### Adding New Message Formatters

Create a new formatter in `app/services/message_formatter.py`:

```python
class CustomMessageFormatter(MessageFormatter):
    def _format_title(self, title: str) -> str:
        # Custom title formatting
        return f"*** {title} ***"
```

### Adding New Endpoints

1. Create endpoint in `app/api/v1/endpoints/`
2. Register in `app/api/v1/router.py`

### Adding New Services

1. Create service in `app/services/`
2. Add dependency in `app/api/deps.py`
3. Inject in endpoints

## License

MIT License
