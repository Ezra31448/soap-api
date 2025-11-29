# Database Setup for Enhanced User Management System

This directory contains all the necessary files and scripts to set up, manage, and maintain the PostgreSQL database for the Enhanced User Management System SOAP API.

## Directory Structure

```
database/
├── init/                           # Database initialization scripts
│   ├── 01-init-database.sql         # Main database schema creation
│   └── 02-insert-initial-data.sql   # Initial data population
├── migrations/                      # Database migration system
│   ├── migrate.py                  # Migration manager script
│   ├── 003_add_user_profile_fields.sql  # Sample migration
│   └── 003_rollback.sql            # Rollback script for migration
├── scripts/                        # Database management scripts
│   ├── backup.sh                   # Database backup script
│   ├── restore.sh                  # Database restore script
│   ├── monitor.sh                  # Database monitoring script
│   ├── optimize.sh                  # Database optimization script
│   └── test_connection.py          # Database connection test script
└── README.md                       # This file
```

## Quick Start

### 1. Using Docker Compose (Recommended)

The easiest way to set up the database is using Docker Compose:

```bash
# Start the database services
docker-compose up -d postgres redis

# Check if the database is ready
docker-compose logs postgres

# Run the database connection test
python database/scripts/test_connection.py --save-report
```

### 2. Manual Setup

If you prefer to set up the database manually:

```bash
# Set environment variables
export DB_NAME="user_management_db"
export DB_USER="postgres"
export DB_PASSWORD="your_password"
export DB_HOST="localhost"
export DB_PORT="5432"

# Initialize the database
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

# Run initialization scripts
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/init/01-init-database.sql
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/init/02-insert-initial-data.sql

# Test the connection
python database/scripts/test_connection.py --save-report
```

## Database Schema

The database consists of the following main tables:

### Core Tables
- **users**: User accounts and profile information
- **roles**: User roles (ADMIN, MANAGER, USER)
- **permissions**: System permissions
- **user_roles**: Junction table for user-role assignments
- **role_permissions**: Junction table for role-permission assignments

### Supporting Tables
- **sessions**: User session management
- **audit_logs**: Audit trail for all system actions

### Database Views
- **user_roles_view**: Combined user and role information
- **user_permissions_view**: User permissions through roles
- **active_users_view**: Users with active sessions
- **user_activity_summary_view**: Daily user activity summary

### Stored Procedures
- **get_user_permissions()**: Get all permissions for a user
- **check_user_permission()**: Check if user has specific permission
- **log_audit_event()**: Log an audit event
- **cleanup_expired_sessions()**: Clean up expired sessions
- **cleanup_old_audit_logs()**: Clean up old audit logs

## Database Management Scripts

### Migration Management

The migration system allows you to manage schema changes over time:

```bash
# Create a new migration
python database/migrations/migrate.py create add_new_feature

# Apply pending migrations
python database/migrations/migrate.py migrate

# Check migration status
python database/migrations/migrate.py status

# Rollback to a specific version
python database/migrations/migrate.py rollback 002
```

### Backup and Restore

#### Backup Script

```bash
# Create a full backup
./database/scripts/backup.sh full

# Create schema-only backup
./database/scripts/backup.sh schema

# Create data-only backup
./database/scripts/backup.sh data

# Create all types of backups
./database/scripts/backup.sh all
```

#### Restore Script

```bash
# List available backups
./database/scripts/restore.sh

# Restore from a specific backup
./database/scripts/restore.sh /path/to/backup/file.sql.gz

# Restore to a different database
./database/scripts/restore.sh /path/to/backup/file.sql.gz new_database_name
```

### Database Monitoring

```bash
# Run comprehensive health check
./database/scripts/monitor.sh health

# Monitor database connections
./database/scripts/monitor.sh connections

# Check database size
./database/scripts/monitor.sh size

# Monitor table statistics
./database/scripts/monitor.sh tables

# Check index usage
./database/scripts/monitor.sh indexes

# Identify slow queries
./database/scripts/monitor.sh slow

# Check for locks
./database/scripts/monitor.sh locks

# Monitor cache hit ratios
./database/scripts/monitor.sh cache

# Check autovacuum information
./database/scripts/monitor.sh vacuum

# Analyze table bloat
./database/scripts/monitor.sh bloat

# Generate comprehensive report
./database/scripts/monitor.sh report

# Run all monitoring checks
./database/scripts/monitor.sh all
```

### Database Optimization

```bash
# Analyze table statistics
./database/scripts/optimize.sh analyze

# Vacuum all tables
./database/scripts/optimize.sh vacuum

# Reindex all tables
./database/scripts/optimize.sh reindex

# Create missing indexes
./database/scripts/optimize.sh indexes

# Optimize query performance
./database/scripts/optimize.sh queries

# Update table statistics
./database/scripts/optimize.sh stats

# Clean up old data
./database/scripts/optimize.sh cleanup

# Analyze and optimize table bloat
./database/scripts/optimize.sh bloat

# Set up connection pooling configuration
./database/scripts/optimize.sh pooling

# Create performance monitoring view
./database/scripts/optimize.sh monitor

# Generate optimization report
./database/scripts/optimize.sh report

# Run all optimizations
./database/scripts/optimize.sh all
```

### Connection Testing

```bash
# Run all database connection tests
python database/scripts/test_connection.py

# Run tests and save report
python database/scripts/test_connection.py --save-report

# Run tests and save to custom file
python database/scripts/test_connection.py --save-report --report-file custom_report.json
```

## Environment Variables

The following environment variables are used by the database scripts:

- `DB_NAME`: Database name (default: user_management_db)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: postgres)
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `BACKUP_DIR`: Backup directory (default: ./backups)
- `REPORT_DIR`: Report directory (default: ./reports)
- `RETENTION_DAYS`: Number of days to keep backups (default: 30)

## Performance Considerations

### Indexes

The database includes several indexes for optimal performance:

- **Primary key indexes** on all tables
- **Foreign key indexes** on all foreign key columns
- **Composite indexes** for common query patterns
- **Partial indexes** for frequently filtered subsets

### Connection Pooling

For production environments, consider using PgBouncer for connection pooling. The optimization script can generate a sample configuration.

### Monitoring

Regular monitoring is recommended for optimal performance:

1. Monitor cache hit ratios (should be >95%)
2. Check for long-running queries
3. Monitor table bloat
4. Track autovacuum effectiveness
5. Monitor connection usage

### Maintenance

Regular maintenance tasks:

1. Run `VACUUM ANALYZE` regularly
2. Monitor and clean up old data
3. Reindex when necessary
4. Update statistics
5. Check for table bloat

## Security Considerations

1. **Password Security**: Use strong passwords for database users
2. **Network Security**: Restrict database access to trusted networks
3. **Encryption**: Enable SSL for database connections in production
4. **Auditing**: The database includes comprehensive audit logging
5. **Row Level Security**: Consider implementing row-level security for sensitive data

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if PostgreSQL is running and accessible
2. **Permission Denied**: Verify database user permissions
3. **Migration Failures**: Check for syntax errors in migration files
4. **Performance Issues**: Run monitoring and optimization scripts

### Debug Mode

Enable debug mode by setting the following environment variable:

```bash
export APP_DEBUG=true
```

This will provide more detailed error messages in the application logs.

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PgBouncer Documentation](https://pgbouncer.github.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Support

For issues related to the database setup:

1. Check the application logs
2. Run the connection test script
3. Review the monitoring reports
4. Check PostgreSQL logs

## Version History

- **v1.0.0**: Initial database schema and management scripts
- **v1.1.0**: Added migration system and enhanced monitoring
- **v1.2.0**: Added performance optimization scripts