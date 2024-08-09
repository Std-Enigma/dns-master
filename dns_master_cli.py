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
    help=(
        ":toolbox: [underline]DNS Master[/underline] - Your CLI solution for efficient DNS management.\n\n"
        "Easily manage and configure your DNS settings from the command line with [bold]DNS Master[/bold]. This tool offers a streamlined interface for handling DNS configurations, allowing you to add, modify, remove, list, and clear settings with simple commands.\n\n"
        "[bold]How It Works:[/bold]\n"
        "[bold]DNS Master[/bold] uses a file-based database to store DNS configurations, ensuring that your settings are saved persistently. You can perform the following operations:\n"
        "- [green]Add[/green]: Create new DNS configurations with unique identifiers.\n"
        "- [red]Remove[/red]: Delete specific DNS configurations.\n"
        "- [yellow]Modify[/yellow]: Update details of existing configurations.\n"
        "- [cyan]List[/cyan]: View all configurations or filter based on identifiers.\n"
        "- [yellow1]Clear[/yellow1]: Remove all stored DNS configurations.\n\n"
        "[bold]Use Cases:[/bold]\n"
        "Perfect for network administrators, developers, and anyone needing to manage DNS settings efficiently from the command line.\n\n"
        "For more detailed information on each command, use `[bold]dns-master [command] --help[/bold]`.\n\n"
        "[bold]Open Source:[/bold] This tool is open source and licensed under the [bold]GPL[/bold] license. You can visit its repository at [underline]https://github.com/Std-Enigma/dns-master[/underline].\n\n"
        "[bold]Usage Examples:[/bold]\n"
        "1. [green]Add[/green] a DNS configuration:\n   `[bold]dns-master [green]add[/green] google 8.8.8.8 8.8.4.4[/bold]`\n"
        "2. [cyan]List[/cyan] all configurations:\n   `[bold]dns-master [cyan]list[/cyan][/bold]`\n"
        "3. [red]Remove[/red] a DNS configuration [underline]without[/underline] confirmation:\n   `[bold]dns-master [red]remove[/red] --force google[/bold]`\n\n"
        "[bold]Contributing and Support:[/bold]\n"
        "If you would like to contribute or need support, please visit our repository and check the [underline]CONTRIBUTING[/underline] and [underline]ISSUES[/underline] sections.\n\n"
    ),
    no_args_is_help=True,
    chain=True,
)


def print_fail_message(message: str) -> None:
    """
    Prints a failure message to the console in bold, italicized red text.

    Args:
        message (str): The message to display.

    Returns:
        None
    """
    console.print(
        f":x: {message}.",
        style="bold italic red",
        justify="center",
    )


def log_error(e: Exception) -> None:
    """
    Logs an exception to the console with red text and highlights.

    Args:
        e (Exception): The exception to log.

    Returns:
        None
    """
    console.log(
        e, emoji=True, highlight=True, style="bold italic red", justify="center"
    )


def log_failed_operation(message: str, e: Exception) -> None:
    """
    Prints a failure message and logs an exception with details about the failed operation.

    Args:
        message (str): The failure message.
        e (Exception): The exception that occurred.

    Returns:
        None
    """
    print_fail_message(f"{message} Please check the error message below for details")
    log_error(e)


@app.command(
    name="add",
    help="[green]:heavy_plus_sign: [bold]Add[/bold] a new DNS configuration.[/green]\n\n"
    "Use this command to add a new DNS configuration to the system. This command requires a unique identifier and the primary DNS address. "
    "You can also specify an optional secondary DNS address and a description for the configuration.\n\n"
    "Notes:\n"
    "- The `identifier` must be unique. If a configuration with the same identifier already exists, the command will produce an error.\n"
    "- The `description` helps you remember the purpose of the configuration.\n\n"
    "Additional Information:\n"
    "- `--list`, `-l`: If specified, lists configurations based on the given identifier after the addition.\n\n"
    "Examples:\n"
    '  dns-master add --list my_dns 8.8.8.8 8.8.4.4 "Google\'s DNS"\n'
    "  dns-master add example_dns 1.1.1.1\n",
)
def add_config(
    identifier: Annotated[
        str,
        typer.Argument(
            help="A unique identifier for the DNS configuration. This name will be used to reference the configuration later."
        ),
    ],
    primary_address: Annotated[str, typer.Argument()],
    secondary_address: Annotated[
        Optional[str],
        typer.Argument(help="The primary DNS address for the configuration."),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Argument(help="The secondary DNS address for the configuration."),
    ] = None,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
            help="List configurations after the operation.",
        ),
    ] = False,
) -> None:
    """
    Adds a new DNS configuration with the given identifier, primary address, and optional secondary address and description.

    Args:
        identifier (str): Unique identifier for the DNS configuration.
        primary_address (str): Primary DNS address.
        secondary_address (Optional[str]): Secondary DNS address (optional).
        description (Optional[str]): Description of the DNS configuration (optional).
        list_after (bool): If True, lists configurations after the operation (optional).

    Returns:
        None
    """
    try:
        db_manager.add_config(
            identifier, primary_address, secondary_address, description
        )
    except Exception as e:
        log_failed_operation("Failed to add the configuration", e)
    else:
        if list_after:
            list_configs()

        console.print(
            f":heavy_plus_sign: Configuration '{identifier}' has been successfully added.",
            style="bold italic green",
            justify="center",
        )


@app.command(
    name="remove",
    help="[red]:heavy_minus_sign: [bold]Remove[/bold] a DNS configuration by its identifier.[/red]\n\n"
    "This command removes a DNS configuration from the system using its unique identifier. "
    "Notes:\n"
    "- Ensure that the identifier you specify is correct to avoid accidental deletions.\n\n"
    "Additional Information:\n"
    "- `--force`: If specified, skips the confirmation prompt and directly removes the configuration.\n"
    "- `--list`, `-l`: If specified, lists configurations after the removal.\n\n"
    "Examples:\n"
    "  dns-master remove --force my_dns\n"
    "  dns-master remove --list example_dns\n",
)
def remove_config(
    identifier: Annotated[
        str,
        typer.Argument(
            help="The unique identifier of the DNS configuration to be removed."
        ),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt="Are you sure you want to delete this configuration?",
            help="Force deletion without confirmation.",
        ),
    ] = False,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
            help="List configurations after the operation.",
        ),
    ] = False,
) -> None:
    """
    Removes a DNS configuration based on its identifier. Requires confirmation if `force` is set to True.

    Args:
        identifier (str): Unique identifier of the DNS configuration to be removed.
        force (bool): If True, removes configuration without additional confirmation.
        list_after (bool): If True, lists configurations after the operation (optional).

    Returns:
        None
    """
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
    help="[yellow]:gear: [bold]Modify[/bold] an existing DNS configuration.[/yellow]\n\n"
    "This command allows you to update an existing DNS configuration. You can change the identifier, primary address, secondary address, and description.\n\n"
    "Notes:\n"
    "- The `identifier` must already exist in the system to be modified.\n"
    "- Ensure you provide at least one new value to update. If no new values are provided, no changes will be made.\n\n"
    "Additional Information:\n"
    "- `--force`: If specified, skips additional confirmation for the modification.\n"
    "- `--list`, `-l`: If specified, lists configurations after modification.\n\n"
    "Examples:\n"
    "  dns-master modify --force old_dns new_dns 1.1.1.1\n",
)
def modify_config(
    identifier: Annotated[
        str,
        typer.Argument(
            help="The unique identifier of the DNS configuration to be modified. This name is used to find and update the existing configuration."
        ),
    ],
    new_identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="The new identifier for the DNS configuration. If not provided, the existing identifier remains unchanged."
        ),
    ] = None,
    new_primary_address: Annotated[
        Optional[str],
        typer.Argument(
            help="The new primary DNS address. If not provided, the existing address remains unchanged."
        ),
    ] = None,
    new_secondary_address: Annotated[
        Optional[str],
        typer.Argument(
            help="The new secondary DNS address. If not provided, the existing address remains unchanged."
        ),
    ] = None,
    new_description: Annotated[
        Optional[str],
        typer.Argument(
            help="The new description for the DNS configuration. If not provided, the existing description remains unchanged."
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt="Are you sure you want to modify the configuration?",
            help="If set to `True`, the modification will proceed without additional confirmation.",
        ),
    ] = False,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
            help="List configurations after the modification.",
        ),
    ] = False,
) -> None:
    """
    Modifies an existing DNS configuration. You can update the identifier, primary address, secondary address, and description. Requires confirmation if `force` is set to True.

    Args:
        identifier (str): Unique identifier of the DNS configuration to be modified.
        new_identifier (Optional[str]): New identifier (optional).
        new_primary_address (Optional[str]): New primary address (optional).
        new_secondary_address (Optional[str]): New secondary address (optional).
        new_description (Optional[str]): New description (optional).
        force (bool): If True, modifies configuration without additional confirmation.
        list_after (bool): If True, lists configurations after the modification (optional).

    Returns:
        None
    """
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
    help="[cyan]:telescope: [bold]List[/bold] all saved DNS configurations.[/cyan]\n\n"
    "This command lists all DNS configurations stored in the system. You can filter the results by providing an identifier. "
    "If no filter is provided, all configurations will be listed.\n\n"
    "Notes:\n"
    "- Filtering by identifier can help you find specific configurations quickly.\n"
    "- If the filter does not match any identifiers, no results will be shown.\n\n"
    "Examples:\n"
    "  dns-master list\n"
    "  dns-master list my_dns\n"
    "  dns-master list example_dns\n",
)
def list_configs(
    filter: Annotated[
        Optional[str],
        typer.Argument(
            help="A string used to filter the displayed configurations based on their identifier. If not provided, all configurations will be listed.",
        ),
    ] = None
) -> None:
    """
    Lists all DNS configurations or filters configurations based on the provided identifier.

    Args:
        filter (Optional[str]): Filter to display configurations based on their identifier (optional).

    Returns:
        None
    """
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


@app.command(
    name="clear",
    help="[yellow1]:wastebasket: [bold]Clear[/bold] all saved DNS configurations.[/yellow1]\n\n"
    "This command clears all DNS configurations from the system."
    "Notes:\n"
    "- Use the `--force` option with caution, as it will permanently delete all configurations without any further confirmation.\n"
    "- After clearing, the list command can be used to verify that all configurations have been removed.\n\n"
    "Additional Information:\n"
    "- `--force`: If specified, skips the confirmation prompt and clears all configurations.\n"
    "- `--list`, `-l`: If specified, lists configurations after clearing.\n\n"
    "Examples:\n"
    "  dns-master clear --force\n"
    "  dns-master clear --list\n",
)
def clear_configs(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt="Are you sure you want to delete All configurations?",
            help="Force deletion without confirmation.",
        ),
    ] = False,
    list_after: Annotated[
        bool,
        typer.Option(
            "--list",
            "-l",
            help="List configurations after the operation.",
        ),
    ] = False,
) -> None:
    """
    Clears all DNS configurations. Requires confirmation if `force` is set to True.

    Args:
        force (bool): If True, clears all configurations without additional confirmation.
        list_after (bool): If True, lists configurations after clearing (optional).

    Returns:
        None
    """
    if not force:
        print_fail_message("Operation cancelled. No configurations were deleted.")
        return

    try:
        db_manager.clear_configs()
    except Exception as e:
        log_failed_operation("Failed to clear DNS configurations", e)
    else:
        if list_after:
            list_configs()

        console.print(
            ":wastebasket: All DNS configurations have been successfully deleted.",
            style="bold italic green",
            justify="center",
        )


if __name__ == "__main__":
    app()
