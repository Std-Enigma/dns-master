from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

import config
from db_manager import DataBaseManager

console = Console()
db_manager = DataBaseManager(config.USER_DATA_DIRECTORY)
app = typer.Typer(
    name="dns-master",
    rich_markup_mode="rich",
    no_args_is_help=True,
    chain=True,
)


def print_fail_message(message: str) -> None:
    console.print(
        f":x: {message}.",
        style="bold italic red",
        justify="center",
    )


def log_error(e: Exception) -> None:
    console.log(
        e, emoji=True, highlight=True, style="bold italic red", justify="center"
    )


def log_failed_operation(message: str, e: Exception) -> None:
    print_fail_message(f"{message} Please check the error message below for details")
    log_error(e)
if __name__ == "__main__":
    app()
