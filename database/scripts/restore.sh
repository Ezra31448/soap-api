#!/bin/bash
# Database Restore Script for Enhanced User Management System
# This script restores PostgreSQL database from backup files

# Configuration
DB_NAME="${DB_NAME:-user_management_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_question() {
    echo -e "${BLUE}[QUESTION]${NC} $1"
}

# Function to check if PostgreSQL is running
check_postgres() {
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to list available backups
list_backups() {
    print_status "Available backup files:"
    echo "--------------------------"
    
    # List full backups
    if ls "$BACKUP_DIR"/full_backup_*.sql.gz 1> /dev/null 2>&1; then
        echo "Full Backups:"
        ls -la "$BACKUP_DIR"/full_backup_*.sql.gz | while read line; do
            echo "  $line"
        done
    else
        print_warning "No full backups found"
    fi
    
    echo ""
    
    # List schema backups
    if ls "$BACKUP_DIR"/schema_backup_*.sql.gz 1> /dev/null 2>&1; then
        echo "Schema Backups:"
        ls -la "$BACKUP_DIR"/schema_backup_*.sql.gz | while read line; do
            echo "  $line"
        done
    else
        print_warning "No schema backups found"
    fi
    
    echo ""
    
    # List data backups
    if ls "$BACKUP_DIR"/data_backup_*.sql.gz 1> /dev/null 2>&1; then
        echo "Data Backups:"
        ls -la "$BACKUP_DIR"/data_backup_*.sql.gz | while read line; do
            echo "  $line"
        done
    else
        print_warning "No data backups found"
    fi
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

# Function to create a new database
create_new_database() {
    local new_db_name="$1"
    
    print_status "Creating new database: $new_db_name"
    
    if PGPASSWORD="${DB_PASSWORD}" createdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$new_db_name"; then
        print_status "Database created successfully"
        return 0
    else
        print_error "Failed to create database"
        return 1
    fi
}

# Function to drop existing database
drop_existing_database() {
    local db_name="$1"
    
    print_warning "Dropping existing database: $db_name"
    
    # Terminate connections to the database
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$db_name';" >/dev/null 2>&1
    
    # Drop the database
    if PGPASSWORD="${DB_PASSWORD}" dropdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$db_name"; then
        print_status "Database dropped successfully"
        return 0
    else
        print_error "Failed to drop database"
        return 1
    fi
}

# Function to restore from backup
restore_from_backup() {
    local backup_file="$1"
    local target_db="$2"
    
    print_status "Restoring database from backup..."
    
    # Decompress backup if needed
    if [[ "$backup_file" == *.gz ]]; then
        print_status "Decompressing backup file..."
        gunzip -c "$backup_file" > "/tmp/restore_temp.sql"
        backup_file="/tmp/restore_temp.sql"
    fi
    
    # Restore the database
    if PGPASSWORD="${DB_PASSWORD}" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$target_db" \
        --verbose \
        --clean \
        --if-exists \
        --no-owner \
        --no-privileges \
        "$backup_file"; then
        
        print_status "Database restored successfully"
        
        # Clean up temporary file
        rm -f "/tmp/restore_temp.sql"
        
        return 0
    else
        print_error "Failed to restore database"
        
        # Clean up temporary file
        rm -f "/tmp/restore_temp.sql"
        
        return 1
    fi
}

# Function to restore from SQL file
restore_from_sql() {
    local sql_file="$1"
    local target_db="$2"
    
    print_status "Restoring database from SQL file..."
    
    # Decompress SQL file if needed
    if [[ "$sql_file" == *.gz ]]; then
        print_status "Decompressing SQL file..."
        gunzip -c "$sql_file" > "/tmp/restore_temp.sql"
        sql_file="/tmp/restore_temp.sql"
    fi
    
    # Restore the database
    if PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$target_db" \
        -f "$sql_file"; then
        
        print_status "Database restored successfully"
        
        # Clean up temporary file
        rm -f "/tmp/restore_temp.sql"
        
        return 0
    else
        print_error "Failed to restore database"
        
        # Clean up temporary file
        rm -f "/tmp/restore_temp.sql"
        
        return 1
    fi
}

# Function to create restore report
create_restore_report() {
    local backup_file="$1"
    local target_db="$2"
    local report_file="$BACKUP_DIR/restore_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Database Restore Report"
        echo "======================"
        echo "Date: $(date)"
        echo "Source Backup: $backup_file"
        echo "Target Database: $target_db"
        echo "Host: $DB_HOST:$DB_PORT"
        echo ""
        echo "Restore Status: SUCCESS"
        echo ""
        echo "Database Statistics After Restore:"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$target_db" \
            -c "\dt+" 2>/dev/null || echo "Could not retrieve table statistics"
        echo ""
        echo "Database Size After Restore:"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$target_db" \
            -c "SELECT pg_size_pretty(pg_database_size('$target_db'));" 2>/dev/null || echo "Could not retrieve database size"
    } > "$report_file"
    
    print_status "Restore report created: $report_file"
}

# Function to prompt for confirmation
confirm_action() {
    local message="$1"
    local default="${2:-n}"
    
    print_question "$message (y/n) [$default]: "
    read -r response
    
    if [ -z "$response" ]; then
        response="$default"
    fi
    
    case "$response" in
        [Yy]|[Yy][Ee][Ss])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Main script logic
main() {
    print_status "Starting database restore process..."
    
    # Check if PostgreSQL is running
    if ! check_postgres; then
        print_error "PostgreSQL is not running or not accessible"
        exit 1
    fi
    
    # Parse command line arguments
    BACKUP_FILE="$1"
    TARGET_DB="$2"
    
    if [ -z "$BACKUP_FILE" ]; then
        print_error "Backup file not specified"
        echo ""
        echo "Usage: $0 <backup_file> [target_database]"
        echo ""
        list_backups
        exit 1
    fi
    
    # Set target database
    if [ -z "$TARGET_DB" ]; then
        TARGET_DB="$DB_NAME"
    fi
    
    # Check if backup file exists
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    # Verify backup integrity
    if ! verify_backup "$BACKUP_FILE"; then
        print_error "Backup verification failed"
        exit 1
    fi
    
    # Check if target database exists
    if PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -c "SELECT 1 FROM pg_database WHERE datname = '$TARGET_DB'" | grep -q 1; then
        
        print_warning "Target database '$TARGET_DB' already exists"
        
        if confirm_action "Do you want to drop the existing database and restore?"; then
            if ! drop_existing_database "$TARGET_DB"; then
                print_error "Failed to drop existing database"
                exit 1
            fi
            
            if ! create_new_database "$TARGET_DB"; then
                print_error "Failed to create new database"
                exit 1
            fi
        else
            print_status "Restore cancelled"
            exit 0
        fi
    else
        # Create new database
        if ! create_new_database "$TARGET_DB"; then
            print_error "Failed to create new database"
            exit 1
        fi
    fi
    
    # Determine restore method based on file type
    if [[ "$BACKUP_FILE" == *.sql* ]]; then
        # Restore from SQL file
        if ! restore_from_sql "$BACKUP_FILE" "$TARGET_DB"; then
            print_error "Restore failed"
            exit 1
        fi
    else
        # Restore from custom format backup
        if ! restore_from_backup "$BACKUP_FILE" "$TARGET_DB"; then
            print_error "Restore failed"
            exit 1
        fi
    fi
    
    # Create restore report
    create_restore_report "$BACKUP_FILE" "$TARGET_DB"
    
    print_status "Restore process completed successfully"
}

# Run main function with all arguments
main "$@"