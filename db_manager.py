import sqlite3


class DataBaseManager:
    def __init__(self, db_name: str) -> None:
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_table()

    def add_config(
        self,
        name: str,
        primary_address: str,
        secondary_address: str | None = None,
        description: str | None = None,
    ) -> None:
        """Add a new DNS configuration to the database."""
        try:
            if self.config_exists(name):
                raise ValueError(
                    f"A configuration with the name '{name}' already exists."
                )

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
        name: str | None = None,
        primary_address: str | None = None,
        secondary_address: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update a DNS configuration in the database by its identifier (name) or rename it."""
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

    def remove_config(self, name: str) -> None:
        """Delete a DNS configuration from the database by its name."""
        self.cursor.execute("DELETE FROM dns_configs WHERE name = ?", (name,))
        self.connection.commit()

    def clear_configs(self) -> None:
        """Delete all DNS configurations from the database."""
        self.cursor.execute("DELETE FROM dns_configs")
        self.connection.commit()

    def get_configs(self, identifier: str | None = None) -> list[tuple]:
        """Retrieve DNS configurations from the database, optionally filtered by name."""
        query = "SELECT * FROM dns_configs"
        params = ()

        if identifier:
            query += " WHERE name LIKE ?"
            params = (f"%{identifier}%",)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def config_exists(self, name: str) -> bool:
        """Check if a configuration with the given name exists."""
        self.cursor.execute("SELECT 1 FROM dns_configs WHERE name = ?", (name,))
        return self.cursor.fetchone() is not None

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
        """Destructor to close the database connection."""
        if self.connection:
            self.connection.close()
