#!/usr/bin/env python3
"""
Database Migration Manager for Enhanced User Management System
This script manages database schema migrations using PostgreSQL
"""
import os
import sys
import asyncio
import asyncpg
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

# Add src to path to import settings
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.config.settings import settings


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.migrations_dir = Path(__file__).parent
        self.connection = None
    
    async def connect(self):
        """Connect to the database"""
        self.connection = await asyncpg.connect(self.db_url)
        # Ensure migrations table exists
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            await self.connection.close()
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        if not self.connection:
            await self.connect()
        
        rows = await self.connection.fetch(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        return [row['version'] for row in rows]
    
    async def get_pending_migrations(self) -> List[Path]:
        """Get list of pending migration files"""
        applied = await self.get_applied_migrations()
        pending = []
        
        # Get all migration files sorted by version
        migration_files = sorted(
            self.migrations_dir.glob("*.sql"),
            key=lambda x: x.name
        )
        
        for file in migration_files:
            # Skip the migrate.py script itself
            if file.name == "migrate.py":
                continue
            
            # Extract version from filename (format: XXX_description.sql)
            version = file.name.split("_")[0]
            if version not in applied:
                pending.append(file)
        
        return pending
    
    async def apply_migration(self, migration_file: Path):
        """Apply a single migration"""
        if not self.connection:
            await self.connect()
        
        version = migration_file.name.split("_")[0]
        print(f"Applying migration {version}: {migration_file.name}")
        
        # Read migration SQL
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Execute migration in a transaction
        async with self.connection.transaction():
            await self.connection.execute(sql)
            await self.connection.execute(
                "INSERT INTO schema_migrations (version) VALUES ($1)",
                version
            )
        
        print(f"Migration {version} applied successfully")
    
    async def migrate(self):
        """Apply all pending migrations"""
        print("Starting database migration...")
        
        pending = await self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations to apply.")
            return
        
        print(f"Found {len(pending)} pending migrations")
        
        for migration_file in pending:
            await self.apply_migration(migration_file)
        
        print("All migrations applied successfully!")
    
    async def rollback(self, target_version: Optional[str] = None):
        """Rollback to a specific version"""
        print("Rolling back database migrations...")
        
        if not target_version:
            print("Error: Target version is required for rollback")
            return
        
        applied = await self.get_applied_migrations()
        
        if target_version not in applied:
            print(f"Error: Version {target_version} is not in applied migrations")
            return
        
        # Get migrations to rollback (in reverse order)
        to_rollback = []
        for version in reversed(applied):
            if version == target_version:
                break
            to_rollback.append(version)
        
        if not to_rollback:
            print(f"No migrations to rollback to version {target_version}")
            return
        
        print(f"Rolling back {len(to_rollback)} migrations")
        
        # For each migration to rollback, look for a corresponding rollback file
        for version in to_rollback:
            rollback_file = self.migrations_dir / f"{version}_rollback.sql"
            if rollback_file.exists():
                print(f"Rolling back migration {version}")
                with open(rollback_file, 'r') as f:
                    sql = f.read()
                
                async with self.connection.transaction():
                    await self.connection.execute(sql)
                    await self.connection.execute(
                        "DELETE FROM schema_migrations WHERE version = $1",
                        version
                    )
                
                print(f"Migration {version} rolled back successfully")
            else:
                print(f"Warning: No rollback file found for migration {version}")
    
    async def status(self):
        """Show migration status"""
        print("Migration Status:")
        print("-" * 50)
        
        applied = await self.get_applied_migrations()
        pending = await self.get_pending_migrations()
        
        print(f"Applied migrations: {len(applied)}")
        for version in applied:
            print(f"  ✓ {version}")
        
        print(f"\nPending migrations: {len(pending)}")
        for file in pending:
            version = file.name.split("_")[0]
            print(f"  ○ {version} - {file.name}")
    
    async def create_migration(self, name: str):
        """Create a new migration file"""
        # Get next version number
        applied = await self.get_applied_migrations()
        next_version = f"{len(applied) + 1:03d}"
        
        # Create migration file
        migration_file = self.migrations_dir / f"{next_version}_{name}.sql"
        with open(migration_file, 'w') as f:
            f.write(f"-- Migration {next_version}: {name}\n")
            f.write(f"-- Created at: {datetime.now().isoformat()}\n\n")
            f.write("-- Add your migration SQL here\n")
        
        # Create rollback file
        rollback_file = self.migrations_dir / f"{next_version}_rollback.sql"
        with open(rollback_file, 'w') as f:
            f.write(f"-- Rollback for migration {next_version}: {name}\n")
            f.write(f"-- Created at: {datetime.now().isoformat()}\n\n")
            f.write("-- Add your rollback SQL here\n")
        
        print(f"Created migration files:")
        print(f"  Migration: {migration_file}")
        print(f"  Rollback:  {rollback_file}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Apply pending migrations")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument("version", help="Target version to rollback to")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show migration status")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("name", help="Migration name/description")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MigrationManager()
    
    try:
        if args.command == "migrate":
            await manager.migrate()
        elif args.command == "rollback":
            await manager.rollback(args.version)
        elif args.command == "status":
            await manager.status()
        elif args.command == "create":
            await manager.create_migration(args.name)
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())