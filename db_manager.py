import sqlite3
from typing import List, Optional, Tuple


class DataBaseManager:
    def __init__(self, db_name: str) -> None:
        """
        Initialize the DataBaseManager with the given database name.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_table()

    def add_config(
        self,
        name: str,
        primary_address: str,
        secondary_address: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Add a new DNS configuration to the database.

        Args:
            name (str): The name (identifier) for the DNS configuration.
            primary_address (str): The primary DNS address.
            secondary_address (Optional[str], optional): The secondary DNS address (default is None).
            description (Optional[str], optional): A description for the DNS configuration (default is None).

        Raises:
            ValueError: If a configuration with the given name already exists.
            RuntimeError: If a database error occurs.
        """
        if self.config_exists(name):
            raise ValueError(f"A configuration with the name '{name}' already exists.")

        try:
            self.cursor.execute(
                """
                INSERT INTO dns_configs (name, primary_address, secondary_address, description)
                VALUES (?, ?, ?, ?)
                """,
                (name, primary_address, secondary_address, description),
            )
            self.connection.commit()

        except sqlite3.IntegrityError as e:
            raise RuntimeError("Database integrity error occurred.") from e
        except sqlite3.DatabaseError as e:
            raise RuntimeError("A database error occurred.") from e
        except Exception as e:
            raise RuntimeError("An unexpected error occurred.") from e

    def modify_config(
        self,
        identifier: str,
        name: Optional[str] = None,
        primary_address: Optional[str] = None,
        secondary_address: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Update an existing DNS configuration in the database.

        Args:
            identifier (str): The current name (identifier) of the DNS configuration to update.
            name (Optional[str], optional): New name for the DNS configuration (default is None).
            primary_address (Optional[str], optional): New primary DNS address (default is None).
            secondary_address (Optional[str], optional): New secondary DNS address (default is None).
            description (Optional[str], optional): New description for the DNS configuration (default is None).

        Raises:
            ValueError: If the configuration to update does not exist or if a new name already exists.
            RuntimeError: If a database error occurs during the update.
        """
        if not self.config_exists(identifier):
            raise ValueError(
                f"No configuration found with the identifier: {identifier}"
            )

        if name and name != identifier and self.config_exists(name):
            raise ValueError(f"A configuration with the name '{name}' already exists.")

        # Build the update query and parameters
        update_query = "UPDATE dns_configs SET "
        params = []
        if name:
            update_query += "name = ?, "
            params.append(name)
        if primary_address is not None:
            update_query += "primary_address = ?, "
            params.append(primary_address)
        if secondary_address is not None:
            update_query += "secondary_address = ?, "
            params.append(secondary_address)
        if description is not None:
            update_query += "description = ?, "
            params.append(description)
        update_query = update_query.rstrip(", ")  # Remove trailing comma
        update_query += " WHERE name = ?"
        params.append(identifier)

        try:
            self.connection.execute("BEGIN")  # Start a transaction
            self.cursor.execute(update_query, tuple(params))
            if self.cursor.rowcount == 0:
                raise ValueError(
                    f"No configuration found with the identifier: {identifier}"
                )
            self.connection.commit()  # Commit the transaction
        except sqlite3.DatabaseError as e:
            self.connection.rollback()  # Rollback in case of error
            raise RuntimeError("A database error occurred during update.") from e

    def remove_config(self, identifier: str) -> None:
        """
        Delete a DNS configuration from the database by its name.

        Args:
            identifier (str): The name (identifier) of the DNS configuration to delete.

        Raises:
            ValueError: If no configuration is found with the given identifier.
            RuntimeError: If a database error occurs during deletion.
        """
        try:
            # Check if the configuration exists before attempting to delete
            if not self.config_exists(identifier):
                raise ValueError(
                    f"No configuration found with the identifier: {identifier}"
                )

            self.connection.execute("BEGIN")  # Start a transaction
            self.cursor.execute("DELETE FROM dns_configs WHERE name = ?", (identifier,))

            if self.cursor.rowcount == 0:
                raise ValueError(
                    f"No configuration found with the identifier: {identifier}"
                )

            self.connection.commit()  # Commit the transaction
        except sqlite3.DatabaseError as e:
            self.connection.rollback()  # Rollback in case of error
            raise RuntimeError("A database error occurred during deletion.") from e

    def clear_configs(self) -> None:
        """
        Delete all DNS configurations from the database.

        Raises:
            RuntimeError: If a database error occurs while clearing configurations.
        """
        try:
            self.connection.execute("BEGIN")  # Start a transaction
            self.cursor.execute("DELETE FROM dns_configs")
            self.connection.commit()  # Commit the transaction
        except sqlite3.DatabaseError as e:
            self.connection.rollback()  # Rollback in case of error
            raise RuntimeError(
                "A database error occurred while clearing configurations."
            ) from e

    def get_configs(
        self, filter: Optional[str] = None
    ) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
        """
        Retrieve DNS configurations from the database, optionally filtered by name.

        Args:
            filter (Optional[str], optional): The name (identifier) to filter configurations by (default is None).

        Returns:
            List[Tuple[str, str, Optional[str], Optional[str]]]: A list of tuples representing DNS configurations.

        Raises:
            RuntimeError: If a database error occurs while retrieving configurations.
        """
        try:
            query = "SELECT * FROM dns_configs"
            params = ()

            if filter:
                query += " WHERE name LIKE ?"
                params = (f"%{filter}%",)

            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            # Validate results format
            if not all(len(row) == 4 for row in results):
                raise RuntimeError("Unexpected result format in database query.")

            return results
        except sqlite3.DatabaseError as e:
            raise RuntimeError(
                "A database error occurred while retrieving configurations."
            ) from e

    def config_exists(self, name: str) -> bool:
        """
        Check if a DNS configuration with the given name exists.

        Args:
            name (str): The name (identifier) of the DNS configuration to check.

        Returns:
            bool: True if a configuration with the given name exists, False otherwise.

        Raises:
            RuntimeError: If a database error occurs during the check.
        """
        try:
            self.cursor.execute("SELECT 1 FROM dns_configs WHERE name = ?", (name,))
            return self.cursor.fetchone() is not None
        except sqlite3.DatabaseError as e:
            raise RuntimeError(
                "A database error occurred while checking configuration existence."
            ) from e

    def _create_table(self) -> None:
        """Create the DNS configurations table if it doesn't exist."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dns_configs (
                name TEXT NOT NULL UNIQUE,
                primary_address TEXT NOT NULL,
                secondary_address TEXT,
                description TEXT
            )
        """
        )
        self.connection.commit()

    def __del__(self) -> None:
        """Destructor to close the database connection safely."""
        try:
            if self.connection:
                self.connection.close()
        except sqlite3.DatabaseError as e:
            # Handle any database errors that may occur during closing
            print(
                f"Warning: An error occurred while closing the database connection: {e}"
            )
        except Exception as e:
            # Handle unexpected errors during the close operation
            print(
                f"Warning: An unexpected error occurred while closing the database connection: {e}"
            )
