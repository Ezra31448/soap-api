#!/bin/bash
# Database Backup Script for Enhanced User Management System
# This script creates backups of the PostgreSQL database

# Configuration
DB_NAME="${DB_NAME:-user_management_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if PostgreSQL is running
check_postgres() {
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to create full database backup
create_full_backup() {
    local backup_file="$BACKUP_DIR/full_backup_$DATE.sql"
    local compressed_file="$backup_file.gz"
    
    print_status "Creating full database backup..."
    
    # Check if PostgreSQL is running
    if ! check_postgres; then
        print_error "PostgreSQL is not running or not accessible"
        exit 1
    fi
    
    # Create backup
    if PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="$backup_file" \
        --lock-wait-timeout=30000; then
        
        print_status "Full backup created: $backup_file"
        
        # Compress the backup
        gzip "$backup_file"
        print_status "Backup compressed: $compressed_file"
        
        # Create checksum
        sha256sum "$compressed_file" > "$compressed_file.sha256"
        print_status "Checksum created: $compressed_file.sha256"
        
        return 0
    else
        print_error "Failed to create full backup"
        return 1
    fi
}

# Function to create schema-only backup
create_schema_backup() {
    local backup_file="$BACKUP_DIR/schema_backup_$DATE.sql"
    local compressed_file="$backup_file.gz"
    
    print_status "Creating schema-only backup..."
    
    if PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --schema-only \
        --file="$backup_file"; then
        
        print_status "Schema backup created: $backup_file"
        
        # Compress the backup
        gzip "$backup_file"
        print_status "Schema backup compressed: $compressed_file"
        
        # Create checksum
        sha256sum "$compressed_file" > "$compressed_file.sha256"
        print_status "Checksum created: $compressed_file.sha256"
        
        return 0
    else
        print_error "Failed to create schema backup"
        return 1
    fi
}

# Function to create data-only backup
create_data_backup() {
    local backup_file="$BACKUP_DIR/data_backup_$DATE.sql"
    local compressed_file="$backup_file.gz"
    
    print_status "Creating data-only backup..."
    
    if PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --data-only \
        --exclude-table-data=sessions \
        --file="$backup_file"; then
        
        print_status "Data backup created: $backup_file"
        
        # Compress the backup
        gzip "$backup_file"
        print_status "Data backup compressed: $compressed_file"
        
        # Create checksum
        sha256sum "$compressed_file" > "$compressed_file.sha256"
        print_status "Checksum created: $compressed_file.sha256"
        
        return 0
    else
        print_error "Failed to create data backup"
        return 1
    fi
}

# Function to clean up old backups
cleanup_old_backups() {
    print_status "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Remove old backup files
    find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.sha256" -mtime +$RETENTION_DAYS -delete
    
    print_status "Cleanup completed"
}

# Function to verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Verify checksum
    if [ -f "$backup_file.sha256" ]; then
        print_status "Verifying backup integrity..."
        if sha256sum -c "$backup_file.sha256" >/dev/null 2>&1; then
            print_status "Backup integrity verified"
            return 0
        else
            print_error "Backup integrity check failed"
            return 1
        fi
    else
        print_warning "Checksum file not found, skipping integrity check"
        return 0
    fi
}

# Function to create backup report
create_backup_report() {
    local report_file="$BACKUP_DIR/backup_report_$DATE.txt"
    
    {
        echo "Database Backup Report"
        echo "======================"
        echo "Date: $(date)"
        echo "Database: $DB_NAME"
        echo "Host: $DB_HOST:$DB_PORT"
        echo ""
        echo "Backup Files Created:"
        find "$BACKUP_DIR" -name "*_$DATE.*" -type f | sort
        echo ""
        echo "Database Statistics:"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "\dt+" 2>/dev/null || echo "Could not retrieve table statistics"
        echo ""
        echo "Database Size:"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null || echo "Could not retrieve database size"
    } > "$report_file"
    
    print_status "Backup report created: $report_file"
}

# Main script logic
main() {
    print_status "Starting database backup process..."
    
    # Parse command line arguments
    BACKUP_TYPE="${1:-full}"
    
    case "$BACKUP_TYPE" in
        "full")
            create_full_backup
            ;;
        "schema")
            create_schema_backup
            ;;
        "data")
            create_data_backup
            ;;
        "all")
            create_full_backup
            create_schema_backup
            create_data_backup
            ;;
        *)
            print_error "Invalid backup type: $BACKUP_TYPE"
            echo "Usage: $0 [full|schema|data|all]"
            exit 1
            ;;
    esac
    
    # Clean up old backups
    cleanup_old_backups
    
    # Create backup report
    create_backup_report
    
    print_status "Backup process completed successfully"
}

# Run main function with all arguments
main "$@"