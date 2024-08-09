from rich.console import Console

import config
from db_manager import DataBaseManager

console = Console()
db_manager = DataBaseManager(config.USER_DATA_DIRECTORY)
