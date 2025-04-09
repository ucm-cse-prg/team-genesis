import typer
import uvicorn

from app.config import Settings, set_settings, settings

# Create a Typer app instance for building command-line applications.
app = typer.Typer()


@app.command()
def start_server(
    host: str = typer.Option(
        settings.host,
        "--host",
        "-h",
        help="The hostname to bind the server to.",
    ),
    port: int = typer.Option(
        settings.port,
        "--port",
        "-p",
        help="The port on which to run the server.",
    ),
    reload: bool = typer.Option(
        settings.reload,
        "--reload",
        "-r",
        help="Enable or disable automatic reloading of the server.",
    ),
    mongodb_url: str = typer.Option(
        settings.mongodb_url,
        "--mongodb",
        help="The URL of the MongoDB database.",
    ),
    db_name: str = typer.Option(
        settings.db_name,
        "--db-name",
        help="The name of the database.",
    ),
    origins: str = typer.Option(
        "*",
        "--origins",
        "--cors",
        help="The origins of the API.",
    ),
) -> None:
    """
    Start the FastAPI server using uvicorn.
    This command starts the uvicorn server by referencing the FastAPI application
    defined in the app module. It accepts parameters for host, port, reload, and a MongoDB URL.
    Args:
        host (str): The hostname to bind the server to. Defaults to "localhost".
        port (int): The port on which to run the server. Defaults to 8000.
        reload (bool): If True, enables auto-reload for development. Defaults to False.
        mongodb_url (str): MongoDB connection string. Defaults to "mongodb://localhost:27017".
        db_name (str): The name of the database. Defaults to "test_db".
        origins (str): The origins of the API. Defaults to "*".
    """

    set_settings(
        Settings(
            host=host,
            port=port,
            reload=reload,
            mongodb_url=mongodb_url,
            db_name=db_name,
            origins=origins,
        )
    )

    # Start the uvicorn server with the specified parameters.
    uvicorn.run(
        "app.app:app", reload=settings.reload, host=settings.host, port=settings.port
    )
