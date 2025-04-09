# FastAPI Application Template

This repository provides a template for creating a FastAPI application with MongoDB (via Beanie and Motor) integration and includes a command-line interface built with Typer. It also supports Docker containerization and unit testing with pytest, making deployment and development easier.

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Development](#development)
- [Docker](#docker)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This template project demonstrates:

- Asynchronous programming with FastAPI.
- Integration with MongoDB using the Beanie ODM.
- Basic CRUD operations through generic API endpoints.
- A command-line interface (via Typer) for application management.
- Containerization using Docker.
- Testing with pytest and static analysis with Ruff.

These features serve as a starting point for building and scaling your own web applications.

## Project Structure

```
fastapi-app/
├── app
│   ├── api.py             # API endpoints (generic GET, POST, PATCH, DELETE)
│   ├── actions.py         # Business logic operations
│   ├── cli.py             # CLI commands using Typer
│   ├── config.py          # Application configuration (MongoDB, server settings, etc.)
│   ├── dependencies.py    # Dependency injection and error handling decorators
│   ├── documents.py       # Database document schemas (Beanie and Pydantic models)
│   ├── exceptions.py      # Custom exception classes for error handling
│   ├── mongo.py           # MongoDB connection initialization and Beanie setup
│   ├── models.py          # Pydantic models for application data
│   └── schemas.py         # Request and response schemas for API endpoints
├── tests
│   ├── conftest.py        # Pytest fixtures (async HTTP client, event loop configuration)
│   └── test_api.py        # API endpoint tests (CRUD operations)
├── Dockerfile             # Containerization instructions for the application
├── docker-compose.yml     # Multi-service configuration (app and MongoDB)
├── requirements.txt       # Python dependencies
├── mypy.ini               # MyPy configuration for static type checking
└── README.md              # Project documentation (this file)
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ucm-cse-prg/{{ (github.repository.split('/'))[1] }}.git
   cd {{ (github.repository.split('/'))[1] }}
   ```

2. **Install UV:**

   [Install UV](https://docs.astral.sh/uv/getting-started/installation/)

   For MacOS/Linux, run:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install the dependencies:**

   ```bash
   uv sync
   ```

## Usage

### Configuration

Application settings are managed in `app/config.py` and can be customized via environment variables or a `.env` file.

Example `.env` file:

```plaintext
MONGODB_URL=mongodb://localhost:27017
PORT=8000
```

### MongoDB Initialization

The MongoDB connection is initialized by the asynchronous `init_mongo()` function in `app/mongo.py`. To run MongoDB locally, you can use Docker:

```bash
docker run -d -p 27017:27017 --name mongodb mongo
```

*Tip: A custom Docker network may be required for proper DNS resolution.*

### Running the Application

Ensure that MongoDB is running on your machine, then start the server in development mode with:

```bash
uv run fastapi-app
```

Additional options can be viewed with:

```bash
uv run fastapi-app --help
```

You can also specify host, port, and MongoDB URL:

```bash
uv run fastapi-app --host <HOST> --port <PORT> --mongodb-url=mongodb://localhost:27017
```

## API Reference

The API is designed to be generic and should follow REST practices.

- **`GET /items/`** – Retrieve a list of items.
- **`GET /items/{id}`** – Retrieve a single item by its ID.
- **`POST /items/`** – Create a new item.
- **`PATCH /items/{id}`** – Update an existing item.
- **`DELETE /items/{id}`** – Delete an item.

You can test the API using the interactive Swagger UI at:  
`http://localhost:8000/docs`

## Development

### IDE Setup

Recommended VSCode extensions for optimal development:
- Python
- Ruff
- MyPy Type Checker
- Pylance
- Copilot/Copilot Chat
- Docker
- MongoDB for VSCode

### Testing

Run the test suite with:

```bash
uv run pytest --cov=app
```

### Linting & Static Analysis

Run Ruff linting:

```bash
uv run ruff check
```

Run type checking with MyPy:

```bash
uv run mypy app
```

## Docker

Build and run the application using Docker:

1. **Build the Docker image:**

   ```bash
   docker build -t {{ (github.repository.split('/'))[1] }} .
   ```

2. **Alternatively, use Docker Compose to run both the app and MongoDB:**

   ```bash
   docker-compose up
   ```

## Contributing

Contributions are welcome! To contribute:

- Open an issue or submit a pull request with improvements or bug fixes.
- Follow the project's coding standards and include tests where applicable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
