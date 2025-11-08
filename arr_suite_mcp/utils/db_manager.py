"""Database management utilities for arr suite."""

import os
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class ArrDatabaseManager:
    """Manager for arr suite database operations."""

    # Database file names for each service
    DATABASE_FILES = {
        "sonarr": "sonarr.db",
        "radarr": "radarr.db",
        "prowlarr": "prowlarr.db",
        "bazarr": "bazarr.db",
    }

    def __init__(self, config_base_path: str = "/opt/docker-media-server/config"):
        """
        Initialize database manager.

        Args:
            config_base_path: Base path where arr config directories are located
        """
        self.config_base_path = Path(config_base_path)

    def get_db_path(self, service: str) -> Path:
        """
        Get the database path for a service.

        Args:
            service: Service name (sonarr, radarr, prowlarr, bazarr)

        Returns:
            Path to the database file
        """
        if service not in self.DATABASE_FILES:
            raise ValueError(f"Unknown service: {service}")

        db_file = self.DATABASE_FILES[service]
        db_path = self.config_base_path / service / db_file

        return db_path

    async def backup_database(
        self,
        service: str,
        backup_dir: Optional[str] = None
    ) -> Path:
        """
        Backup a service database.

        Args:
            service: Service name
            backup_dir: Directory to store backup (default: config_path/backups)

        Returns:
            Path to backup file
        """
        db_path = self.get_db_path(service)

        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        # Create backup directory
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = self.config_base_path / "backups" / service

        backup_path.mkdir(parents=True, exist_ok=True)

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"{service}_{timestamp}.db"

        logger.info(f"Backing up {service} database to {backup_file}")

        # Copy database file
        shutil.copy2(db_path, backup_file)

        logger.info(f"Backup completed: {backup_file}")

        return backup_file

    async def backup_all(
        self,
        backup_dir: Optional[str] = None
    ) -> dict[str, Path]:
        """
        Backup all service databases.

        Args:
            backup_dir: Directory to store backups

        Returns:
            Dictionary mapping service names to backup file paths
        """
        backups = {}

        for service in self.DATABASE_FILES.keys():
            try:
                backup_file = await self.backup_database(service, backup_dir)
                backups[service] = backup_file
            except FileNotFoundError:
                logger.warning(f"Database for {service} not found, skipping")
            except Exception as e:
                logger.error(f"Failed to backup {service}: {e}")

        return backups

    async def restore_database(
        self,
        service: str,
        backup_file: str,
        create_backup: bool = True
    ) -> None:
        """
        Restore a database from backup.

        Args:
            service: Service name
            backup_file: Path to backup file
            create_backup: Whether to backup current database first
        """
        db_path = self.get_db_path(service)
        backup_path = Path(backup_file)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        # Backup current database if it exists
        if create_backup and db_path.exists():
            logger.info(f"Creating backup of current {service} database")
            await self.backup_database(service)

        # Restore from backup
        logger.info(f"Restoring {service} database from {backup_file}")
        shutil.copy2(backup_path, db_path)

        logger.info(f"Database restored successfully")

    async def execute_query(
        self,
        service: str,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> Any:
        """
        Execute a SQL query on a service database.

        Args:
            service: Service name
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results if fetch=True
        """
        db_path = self.get_db_path(service)

        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                results = [dict(row) for row in cursor.fetchall()]
                return results
            else:
                conn.commit()
                return cursor.rowcount

        finally:
            conn.close()

    async def get_table_info(
        self,
        service: str,
        table_name: str
    ) -> list[dict[str, Any]]:
        """
        Get schema information for a table.

        Args:
            service: Service name
            table_name: Table name

        Returns:
            List of column information
        """
        query = f"PRAGMA table_info({table_name})"
        return await self.execute_query(service, query)

    async def list_tables(self, service: str) -> list[str]:
        """
        List all tables in a service database.

        Args:
            service: Service name

        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        results = await self.execute_query(service, query)
        return [row["name"] for row in results]

    async def vacuum_database(self, service: str) -> None:
        """
        Vacuum (optimize) a service database.

        Args:
            service: Service name
        """
        db_path = self.get_db_path(service)

        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        logger.info(f"Vacuuming {service} database")

        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("VACUUM")
            conn.commit()
            logger.info(f"Database vacuumed successfully")
        finally:
            conn.close()

    async def get_database_size(self, service: str) -> int:
        """
        Get database file size in bytes.

        Args:
            service: Service name

        Returns:
            File size in bytes
        """
        db_path = self.get_db_path(service)

        if not db_path.exists():
            return 0

        return db_path.stat().st_size

    async def get_all_database_sizes(self) -> dict[str, dict[str, Any]]:
        """
        Get sizes of all service databases.

        Returns:
            Dictionary with database size information
        """
        sizes = {}

        for service in self.DATABASE_FILES.keys():
            size_bytes = await self.get_database_size(service)
            size_mb = size_bytes / (1024 * 1024)

            sizes[service] = {
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 2),
                "size_human": self._human_readable_size(size_bytes)
            }

        return sizes

    @staticmethod
    def _human_readable_size(size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
