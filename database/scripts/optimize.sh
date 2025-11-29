#!/bin/bash
# Database Performance Optimization Script for Enhanced User Management System
# This script optimizes PostgreSQL database performance

# Configuration
DB_NAME="${DB_NAME:-user_management_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

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

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check if PostgreSQL is running
check_postgres() {
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to analyze table statistics
analyze_tables() {
    print_header "Analyzing Table Statistics"
    echo "================================"
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "ANALYZE;"
    
    print_status "Table statistics updated"
    echo ""
}

# Function to vacuum tables
vacuum_tables() {
    print_header "Vacuuming Tables"
    echo "==================="
    
    local tables=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | tr -d ' ')
    
    for table in $tables; do
        print_status "Vacuuming table: $table"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "VACUUM (VERBOSE, ANALYZE) $table;" >/dev/null 2>&1
    done
    
    print_status "All tables vacuumed"
    echo ""
}

# Function to reindex tables
reindex_tables() {
    print_header "Reindexing Tables"
    echo "===================="
    
    local tables=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | tr -d ' ')
    
    for table in $tables; do
        print_status "Reindexing table: $table"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "REINDEX TABLE $table;" >/dev/null 2>&1
    done
    
    print_status "All tables reindexed"
    echo ""
}

# Function to create missing indexes
create_missing_indexes() {
    print_header "Creating Missing Indexes"
    echo "==========================="
    
    # Check for foreign key indexes
    print_status "Checking for foreign key indexes..."
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        -- Create index for user_roles.user_id if not exists
        DO \$\$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'user_roles' AND indexname = 'idx_user_roles_user_id'
            ) THEN
                CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
                RAISE NOTICE 'Created index idx_user_roles_user_id';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'user_roles' AND indexname = 'idx_user_roles_role_id'
            ) THEN
                CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
                RAISE NOTICE 'Created index idx_user_roles_role_id';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'role_permissions' AND indexname = 'idx_role_permissions_role_id'
            ) THEN
                CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
                RAISE NOTICE 'Created index idx_role_permissions_role_id';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'role_permissions' AND indexname = 'idx_role_permissions_permission_id'
            ) THEN
                CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
                RAISE NOTICE 'Created index idx_role_permissions_permission_id';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'audit_logs' AND indexname = 'idx_audit_logs_user_action_date'
            ) THEN
                CREATE INDEX idx_audit_logs_user_action_date ON audit_logs(user_id, action, created_at);
                RAISE NOTICE 'Created index idx_audit_logs_user_action_date';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'audit_logs' AND indexname = 'idx_audit_logs_resource_date'
            ) THEN
                CREATE INDEX idx_audit_logs_resource_date ON audit_logs(resource_type, resource_id, created_at);
                RAISE NOTICE 'Created index idx_audit_logs_resource_date';
            END IF;
        END \$\$;
        "
    
    print_status "Missing indexes check completed"
    echo ""
}

# Function to create partial indexes for better performance
create_partial_indexes() {
    print_header "Creating Partial Indexes"
    echo "========================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        -- Create partial index for active users
        DO \$\$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'users' AND indexname = 'idx_users_active'
            ) THEN
                CREATE INDEX idx_users_active ON users(id) WHERE status = 'ACTIVE';
                RAISE NOTICE 'Created partial index idx_users_active';
            END IF;
            
            -- Create partial index for recent audit logs
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'audit_logs' AND indexname = 'idx_audit_logs_recent'
            ) THEN
                CREATE INDEX idx_audit_logs_recent ON audit_logs(created_at) 
                WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '30 days';
                RAISE NOTICE 'Created partial index idx_audit_logs_recent';
            END IF;
            
            -- Create partial index for active sessions
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = 'sessions' AND indexname = 'idx_sessions_active'
            ) THEN
                CREATE INDEX idx_sessions_active ON sessions(user_id, expires_at) 
                WHERE expires_at > CURRENT_TIMESTAMP;
                RAISE NOTICE 'Created partial index idx_sessions_active';
            END IF;
        END \$\$;
        "
    
    print_status "Partial indexes created"
    echo ""
}

# Function to optimize query performance
optimize_queries() {
    print_header "Optimizing Query Performance"
    echo "================================="
    
    # Enable pg_stat_statements if not already enabled
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        -- Enable pg_stat_statements extension if not exists
        CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
        
        -- Reset statistics
        SELECT pg_stat_statements_reset();
        " 2>/dev/null
    
    print_status "Query optimization settings applied"
    echo ""
}

# Function to update table statistics
update_statistics() {
    print_header "Updating Table Statistics"
    echo "=============================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        -- Update statistics for all tables
        DO \$\$
        DECLARE
            table_record RECORD;
        BEGIN
            FOR table_record IN 
                SELECT tablename FROM pg_tables WHERE schemaname = 'public'
            LOOP
                EXECUTE 'ANALYZE ' || table_record.tablename;
                RAISE NOTICE 'Analyzed table: %', table_record.tablename;
            END LOOP;
        END \$\$;
        "
    
    print_status "Table statistics updated"
    echo ""
}

# Function to clean up old data
cleanup_old_data() {
    print_header "Cleaning Up Old Data"
    echo "======================="
    
    # Clean up expired sessions
    local expired_sessions=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "
        SELECT cleanup_expired_sessions();
        " 2>/dev/null | tr -d ' ')
    
    print_status "Cleaned up $expired_sessions expired sessions"
    
    # Clean up old audit logs (older than 1 year)
    local old_audit_logs=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "
        SELECT cleanup_old_audit_logs();
        " 2>/dev/null | tr -d ' ')
    
    print_status "Cleaned up $old_audit_logs old audit log entries"
    echo ""
}

# Function to check and optimize table bloat
optimize_bloat() {
    print_header "Optimizing Table Bloat"
    echo "========================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        -- Identify tables with high bloat
        WITH bloat_info AS (
            SELECT 
                schemaname,
                tablename,
                ROUND((
                    CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END
                )::numeric,1) AS tbloat,
                CASE WHEN relpages < otta THEN 0 ELSE relpages::bigint - otta END AS wastedpages
            FROM (
                SELECT 
                    i.nspname AS schemaname,
                    c.relname AS tablename,
                    c.reltuples,
                    c.relpages,
                    bs,
                    CEIL((c.reltuples*((datahdr+ma-
                        (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta
                FROM (
                    SELECT 
                        ma,bs,pages,datahdr,ma,(
                        CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 0 END
                    ) AS nullhdr2
                    FROM (
                        SELECT 
                            tablespace_id AS id,
                            CASE WHEN relpersistence='t' THEN 9 ELSE 8 END AS ma,
                            8192 AS bs,
                            CASE WHEN version()~'mingw32' THEN 8 ELSE 4 END AS pages,
                            32 AS datahdr,
                            24 AS ma
                    ) AS foo
                    CROSS JOIN (
                        SELECT 
                            (regexp_split_to_array(v, ' '))[2] AS version
                        FROM version() AS v
                    ) AS ver
                ) AS constants,
                pg_class c
                LEFT JOIN pg_index i ON c.oid = i.indrelid
                WHERE c.relkind IN ('r')
            ) AS sml
            WHERE sml.relpages > 0
        )
        SELECT schemaname, tablename, tbloat, wastedpages
        FROM bloat_info
        WHERE tbloat > 1.5 OR wastedpages > 10
        ORDER BY wastedpages DESC
        LIMIT 10;
        " 2>/dev/null
    
    print_status "Bloat analysis completed"
    echo ""
}

# Function to set up connection pooling
setup_connection_pooling() {
    print_header "Connection Pooling Configuration"
    echo "===================================="
    
    print_warning "Connection pooling requires PgBouncer to be installed separately"
    print_status "Sample PgBouncer configuration:"
    echo ""
    echo "[databases]"
    echo "$DB_NAME = host=$DB_HOST port=$DB_PORT dbname=$DB_NAME"
    echo ""
    echo "[pgbouncer]"
    echo "listen_port = 6432"
    echo "listen_addr = 127.0.0.1"
    echo "auth_type = md5"
    echo "auth_file = /etc/pgbouncer/userlist.txt"
    echo "logfile = /var/log/pgbouncer/pgbouncer.log"
    echo "pidfile = /var/run/pgbouncer/pgbouncer.pid"
    echo "admin_users = postgres"
    echo "stats_users = stats, postgres"
    echo "pool_mode = transaction"
    echo "max_client_conn = 100"
    echo "default_pool_size = 20"
    echo "min_pool_size = 5"
    echo "reserve_pool_size = 5"
    echo "reserve_pool_timeout = 5"
    echo "max_db_connections = 50"
    echo "max_user_connections = 50"
    echo "server_reset_query = DISCARD ALL"
    echo "ignore_startup_parameters = extra_float_digits"
    echo ""
}

# Function to create performance monitoring view
create_performance_view() {
    print_header "Creating Performance Monitoring View"
    echo "======================================"
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        -- Create or replace performance monitoring view
        CREATE OR REPLACE VIEW performance_monitoring_view AS
        SELECT 
            'database_size' as metric,
            pg_size_pretty(pg_database_size('$DB_NAME')) as value,
            pg_database_size('$DB_NAME') as value_bytes
        UNION ALL
        SELECT 
            'active_connections' as metric,
            COUNT(*)::text as value,
            COUNT(*) as value_bytes
        FROM pg_stat_activity 
        WHERE datname = '$DB_NAME' AND state = 'active'
        UNION ALL
        SELECT 
            'table_cache_hit_ratio' as metric,
            ROUND(sum(heap_blks_hit)::numeric / 
                  (sum(heap_blks_hit) + sum(heap_blks_read)), 4) * 100 || '%' as value,
            ROUND(sum(heap_blks_hit)::numeric / 
                  (sum(heap_blks_hit) + sum(heap_blks_read)), 4) * 100 as value_bytes
        FROM pg_stat_user_tables
        UNION ALL
        SELECT 
            'index_cache_hit_ratio' as metric,
            ROUND(sum(idx_blks_hit)::numeric / 
                  (sum(idx_blks_hit) + sum(idx_blks_read)), 4) * 100 || '%' as value,
            ROUND(sum(idx_blks_hit)::numeric / 
                  (sum(idx_blks_hit) + sum(idx_blks_read)), 4) * 100 as value_bytes
        FROM pg_stat_user_indexes;
        "
    
    print_status "Performance monitoring view created"
    echo ""
}

# Function to generate optimization report
generate_optimization_report() {
    local report_file="./reports/optimization_report_$(date +%Y%m%d_%H%M%S).txt"
    
    print_status "Generating optimization report..."
    
    {
        echo "Database Optimization Report"
        echo "==========================="
        echo "Date: $(date)"
        echo "Database: $DB_NAME"
        echo "Host: $DB_HOST:$DB_PORT"
        echo ""
        
        echo "Database Size:"
        echo "=============="
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "
            SELECT 
                pg_size_pretty(pg_database_size('$DB_NAME')) as total_size;
            " 2>/dev/null
        echo ""
        
        echo "Table Statistics:"
        echo "================"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "
            SELECT 
                tablename,
                n_live_tup as live_rows,
                n_dead_tup as dead_rows,
                last_vacuum,
                last_autovacuum
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC;
            " 2>/dev/null
        echo ""
        
        echo "Index Usage:"
        echo "============"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "
            SELECT 
                tablename,
                indexname,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            LIMIT 20;
            " 2>/dev/null
        echo ""
        
    } > "$report_file"
    
    print_status "Optimization report generated: $report_file"
}

# Main script logic
main() {
    print_status "Starting database optimization..."
    
    # Check if PostgreSQL is running
    if ! check_postgres; then
        print_error "PostgreSQL is not running or not accessible"
        exit 1
    fi
    
    # Create reports directory if it doesn't exist
    mkdir -p ./reports
    
    # Parse command line arguments
    OPTIMIZE_TYPE="${1:-all}"
    
    case "$OPTIMIZE_TYPE" in
        "analyze")
            analyze_tables
            ;;
        "vacuum")
            vacuum_tables
            ;;
        "reindex")
            reindex_tables
            ;;
        "indexes")
            create_missing_indexes
            create_partial_indexes
            ;;
        "queries")
            optimize_queries
            ;;
        "stats")
            update_statistics
            ;;
        "cleanup")
            cleanup_old_data
            ;;
        "bloat")
            optimize_bloat
            ;;
        "pooling")
            setup_connection_pooling
            ;;
        "monitor")
            create_performance_view
            ;;
        "report")
            generate_optimization_report
            ;;
        "all")
            analyze_tables
            vacuum_tables
            create_missing_indexes
            create_partial_indexes
            optimize_queries
            update_statistics
            cleanup_old_data
            create_performance_view
            generate_optimization_report
            ;;
        *)
            print_error "Invalid optimization type: $OPTIMIZE_TYPE"
            echo "Usage: $0 [analyze|vacuum|reindex|indexes|queries|stats|cleanup|bloat|pooling|monitor|report|all]"
            exit 1
            ;;
    esac
    
    print_status "Database optimization completed"
}

# Run main function with all arguments
main "$@"