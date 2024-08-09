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


@app.command(
    name="add",
)
def add_config(
    identifier: Annotated[
        str,
        typer.Argument(),
    ],
    primary_address: Annotated[str, typer.Argument()],
    secondary_address: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
        ),
    ] = False,
) -> None:
    try:
        db_manager.add_config(
            identifier, primary_address, secondary_address, description
        )
    except Exception as e:
        log_failed_operation("Failed to add the configuration", e)
    else:
        if list_after:
            list_configs(identifier)

        console.print(
            f":heavy_plus_sign: Configuration '{identifier}' has been successfully added.",
            style="bold italic green",
            justify="center",
        )


@app.command(
    name="remove",
)
def remove_config(
    identifier: Annotated[
        str,
        typer.Argument(),
    ],
    force: Annotated[
        bool,
        typer.Option(
            prompt="Are you sure you want to delete this configuration?",
        ),
    ] = False,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
        ),
    ] = False,
) -> None:
    if not force:
        print_fail_message("Operation cancelled. No configurations were deleted.")
        return

    try:
        db_manager.remove_config(identifier)
    except Exception as e:
        log_failed_operation("Failed to remove the configuration", e)
    else:
        if list_after:
            list_configs()

        console.print(
            f":heavy_minus_sign: Configuration '{identifier}' has been successfully removed.",
            style="bold italic green",
            justify="center",
        )


@app.command(
    name="modify",
)
def modify_config(
    identifier: Annotated[
        str,
        typer.Argument(),
    ],
    new_identifier: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None,
    new_primary_address: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None,
    new_secondary_address: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None,
    new_description: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            prompt="Are you sure you want to modify the configuration?",
        ),
    ] = False,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
        ),
    ] = False,
) -> None:
    if not force:
        print_fail_message("Operation cancelled. No configurations were modified")
        return

    try:
        db_manager.modify_config(
            identifier,
            new_identifier,
            new_primary_address,
            new_secondary_address,
            new_description,
        )
    except Exception as e:
        log_failed_operation("Failed to modify DNS configuration", e)
    else:
        if list_after:
            list_configs()

        console.print(
            f":gear: Configuration '{identifier}' has been successfully modified",
            style="bold green",
            justify="center",
        )


@app.command(
    name="list",
)
def list_configs(
    filter: Annotated[
        Optional[str],
        typer.Argument(),
    ] = None
) -> None:
    configs_table = Table(
        title=(
            f":telescope: DNS Configurations"
            + f" - Results for '[bold]{filter}[/bold]' :mag_right:"
            if filter
            else None
        ),
        border_style="cyan",
        header_style="bold italic",
    )

    configs_table.add_column("Identifier", header_style="green", justify="left")
    configs_table.add_column(
        "Primary Address",
        header_style="blue",
        justify="center",
    )
    configs_table.add_column(
        "Secondary Address",
        header_style="red",
        justify="center",
    )
    configs_table.add_column(
        "Description",
        header_style="yellow",
        justify="center",
    )

    try:
        configs = db_manager.get_configs(filter)
    except Exception as e:
        log_failed_operation("Failed to retrieve the DNS configurations", e)
        return

    for config in configs:
        identifier, primary_address, secondary_address, description = (
            config[0],
            config[1],
            config[2] or "",
            config[3] or "No Description",
        )
        configs_table.add_row(
            identifier,
            primary_address,
            secondary_address,
            description,
        )
        configs_table.add_section()

    console.print(configs_table, justify="center")
if __name__ == "__main__":
    app()
