#!/bin/bash
# Database Monitoring Script for Enhanced User Management System
# This script monitors PostgreSQL database performance and health

# Configuration
DB_NAME="${DB_NAME:-user_management_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
REPORT_DIR="${REPORT_DIR:-./reports}"
DATE=$(date +%Y%m%d_%H%M%S)

# Create report directory if it doesn't exist
mkdir -p "$REPORT_DIR"

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

# Function to get database connections
get_connections() {
    print_header "Database Connections"
    echo "========================"
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            state,
            COUNT(*) as connection_count,
            MAX(now() - state_change) as longest_state_duration
        FROM pg_stat_activity 
        WHERE datname = '$DB_NAME'
        GROUP BY state
        ORDER BY connection_count DESC;
        "
    
    echo ""
}

# Function to get database size information
get_database_size() {
    print_header "Database Size Information"
    echo "============================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            pg_database_size('$DB_NAME') as total_size_bytes,
            pg_size_pretty(pg_database_size('$DB_NAME')) as total_size;
        "
    
    echo ""
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as data_size,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 10;
        "
    
    echo ""
}

# Function to get table statistics
get_table_stats() {
    print_header "Table Statistics"
    echo "==================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC;
        "
    
    echo ""
}

# Function to get index usage statistics
get_index_usage() {
    print_header "Index Usage Statistics"
    echo "==========================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read as index_reads,
            idx_tup_fetch as index_fetches,
            idx_scan as index_scans
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC
        LIMIT 20;
        "
    
    echo ""
}

# Function to get slow queries
get_slow_queries() {
    print_header "Slow Queries"
    echo "============="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows
        FROM pg_stat_statements 
        WHERE mean_time > 1000
        ORDER BY mean_time DESC
        LIMIT 10;
        " 2>/dev/null || print_warning "pg_stat_statements extension not enabled"
    
    echo ""
}

# Function to get lock information
get_locks() {
    print_header "Lock Information"
    echo "=================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            t.relname as table_name,
            l.locktype,
            l.mode,
            l.granted,
            a.query,
            a.age as query_age
        FROM pg_locks l
        JOIN pg_stat_activity a ON l.pid = a.pid
        LEFT JOIN pg_class t ON l.relation = t.oid
        WHERE l.database = (SELECT oid FROM pg_database WHERE datname = '$DB_NAME')
        AND NOT l.granted
        ORDER BY a.age DESC;
        "
    
    echo ""
}

# Function to get checkpoint statistics
get_checkpoint_stats() {
    print_header "Checkpoint Statistics"
    echo "========================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            checkpoints_timed,
            checkpoints_req,
            checkpoint_write_time,
            checkpoint_sync_time,
            buffers_checkpoint,
            buffers_clean,
            maxwritten_clean,
            buffers_backend,
            buffers_backend_fsync,
            buffers_alloc
        FROM pg_stat_bgwriter;
        "
    
    echo ""
}

# Function to get cache hit ratios
get_cache_hit_ratios() {
    print_header "Cache Hit Ratios"
    echo "==================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            'index hit ratio' as metric,
            round(sum(idx_blks_hit)::numeric / 
                  (sum(idx_blks_hit) + sum(idx_blks_read)), 4) * 100 as percentage
        FROM pg_stat_user_indexes
        UNION ALL
        SELECT 
            'table hit ratio' as metric,
            round(sum(heap_blks_hit)::numeric / 
                  (sum(heap_blks_hit) + sum(heap_blks_read)), 4) * 100 as percentage
        FROM pg_stat_user_tables;
        "
    
    echo ""
}

# Function to get replication lag (if applicable)
get_replication_lag() {
    print_header "Replication Information"
    echo "========================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            application_name,
            client_addr,
            state,
            sync_priority,
            sync_state,
            pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) as replication_lag
        FROM pg_stat_replication;
        " 2>/dev/null || print_warning "No replication configured or insufficient privileges"
    
    echo ""
}

# Function to get autovacuum information
get_autovacuum_info() {
    print_header "Autovacuum Information"
    echo "========================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            relname,
            last_vacuum,
            last_autovacuum,
            vacuum_count,
            autovacuum_count,
            last_analyze,
            last_autoanalyze,
            analyze_count,
            autoanalyze_count
        FROM pg_stat_user_tables
        WHERE autovacuum_count > 0 OR analyze_count > 0
        ORDER BY autovacuum_count DESC
        LIMIT 10;
        "
    
    echo ""
}

# Function to check for bloat
check_bloat() {
    print_header "Table Bloat Analysis"
    echo "======================="
    
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "
        SELECT 
            current_database(),
            schemaname,
            tablename,
            ROUND((
                CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END
            )::numeric,1) AS tbloat,
            CASE WHEN relpages < otta THEN 0 ELSE relpages::bigint - otta END AS wastedpages,
            CASE WHEN relpages < otta THEN 0 ELSE bs*(sml.relpages-otta)::bigint END AS wastedbytes,
            CASE WHEN relpages < otta THEN 0 ELSE (bs*(relpages-otta))::bigint END AS wastedsize,
            iname,
            ROUND((
                CASE WHEN iotta=0 OR ipages=0 THEN 0.0 ELSE ipages/iotta::numeric END
            )::numeric,1) AS ibloat,
            CASE WHEN ipages < iotta THEN 0 ELSE ipages::bigint - iotta END AS wastedipages,
            CASE WHEN ipages < iotta THEN 0 ELSE bs*(ipages-iotta) END AS wastedibytes
        FROM (
            SELECT 
                i.nspname AS schemaname,
                c.relname AS tablename,
                c.reltuples,
                c.relpages,
                bs,
                CEIL((c.reltuples*((datahdr+ma-
                    (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta,
                COALESCE(c2.relname,'?') AS iname,
                COALESCE(c2.reltuples,0) AS ituples,
                COALESCE(c2.relpages,0) AS ipages,
                COALESCE(CEIL((c2.reltuples*(datahdr-12))/(bs-20::float)),0) AS iotta
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
            LEFT JOIN pg_class c2 ON c2.oid = i.indexrelid
            WHERE c.relkind IN ('r','i')
        ) AS sml
        WHERE sml.relpages > 0
        ORDER BY wastedibytes DESC
        LIMIT 10;
        " 2>/dev/null || print_warning "Bloat analysis query failed"
    
    echo ""
}

# Function to generate comprehensive report
generate_report() {
    local report_file="$REPORT_DIR/database_monitor_report_$DATE.txt"
    
    print_status "Generating comprehensive database report..."
    
    {
        echo "Database Monitoring Report"
        echo "========================"
        echo "Date: $(date)"
        echo "Database: $DB_NAME"
        echo "Host: $DB_HOST:$DB_PORT"
        echo ""
        
        # Database connections
        echo "DATABASE CONNECTIONS"
        echo "==================="
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "
            SELECT 
                state,
                COUNT(*) as connection_count
            FROM pg_stat_activity 
            WHERE datname = '$DB_NAME'
            GROUP BY state
            ORDER BY connection_count DESC;
            " 2>/dev/null
        echo ""
        
        # Database size
        echo "DATABASE SIZE"
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
        
        # Table statistics
        echo "TABLE STATISTICS"
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
            ORDER BY n_live_tup DESC
            LIMIT 10;
            " 2>/dev/null
        echo ""
        
        # Cache hit ratios
        echo "CACHE HIT RATIOS"
        echo "================"
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "
            SELECT 
                'index hit ratio' as metric,
                round(sum(idx_blks_hit)::numeric / 
                      (sum(idx_blks_hit) + sum(idx_blks_read)), 4) * 100 as percentage
            FROM pg_stat_user_indexes
            UNION ALL
            SELECT 
                'table hit ratio' as metric,
                round(sum(heap_blks_hit)::numeric / 
                      (sum(heap_blks_hit) + sum(heap_blks_read)), 4) * 100 as percentage
            FROM pg_stat_user_tables;
            " 2>/dev/null
        echo ""
        
    } > "$report_file"
    
    print_status "Report generated: $report_file"
}

# Function to check database health
check_health() {
    print_header "Database Health Check"
    echo "======================="
    
    local health_issues=0
    
    # Check if PostgreSQL is running
    if ! check_postgres; then
        print_error "PostgreSQL is not running or not accessible"
        health_issues=$((health_issues + 1))
    else
        print_status "PostgreSQL is running"
    fi
    
    # Check database connections
    local active_connections=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND state = 'active';" 2>/dev/null | tr -d ' ')
    
    if [ "$active_connections" -gt 80 ]; then
        print_warning "High number of active connections: $active_connections"
        health_issues=$((health_issues + 1))
    else
        print_status "Active connections: $active_connections"
    fi
    
    # Check for long-running queries
    local long_queries=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND state = 'active' AND now() - query_start > interval '5 minutes';" 2>/dev/null | tr -d ' ')
    
    if [ "$long_queries" -gt 0 ]; then
        print_warning "Long-running queries detected: $long_queries"
        health_issues=$((health_issues + 1))
    else
        print_status "No long-running queries detected"
    fi
    
    # Check for locks
    local locks=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "SELECT COUNT(*) FROM pg_locks WHERE NOT granted;" 2>/dev/null | tr -d ' ')
    
    if [ "$locks" -gt 0 ]; then
        print_warning "Waiting locks detected: $locks"
        health_issues=$((health_issues + 1))
    else
        print_status "No waiting locks detected"
    fi
    
    # Check cache hit ratios
    local table_hit_ratio=$(PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "
        SELECT round(sum(heap_blks_hit)::numeric / 
              (sum(heap_blks_hit) + sum(heap_blks_read)), 4) * 100
        FROM pg_stat_user_tables;" 2>/dev/null | tr -d ' ')
    
    if [ -n "$table_hit_ratio" ] && (( $(echo "$table_hit_ratio < 95" | bc -l) )); then
        print_warning "Low table cache hit ratio: ${table_hit_ratio}%"
        health_issues=$((health_issues + 1))
    else
        print_status "Table cache hit ratio: ${table_hit_ratio}%"
    fi
    
    echo ""
    if [ "$health_issues" -eq 0 ]; then
        print_status "Database health check: PASSED"
    else
        print_warning "Database health check: $health_issues issue(s) detected"
    fi
    
    echo ""
}

# Main script logic
main() {
    print_status "Starting database monitoring..."
    
    # Check if PostgreSQL is running
    if ! check_postgres; then
        print_error "PostgreSQL is not running or not accessible"
        exit 1
    fi
    
    # Parse command line arguments
    MONITOR_TYPE="${1:-all}"
    
    case "$MONITOR_TYPE" in
        "health")
            check_health
            ;;
        "connections")
            get_connections
            ;;
        "size")
            get_database_size
            ;;
        "tables")
            get_table_stats
            ;;
        "indexes")
            get_index_usage
            ;;
        "slow")
            get_slow_queries
            ;;
        "locks")
            get_locks
            ;;
        "cache")
            get_cache_hit_ratios
            ;;
        "vacuum")
            get_autovacuum_info
            ;;
        "bloat")
            check_bloat
            ;;
        "report")
            generate_report
            ;;
        "all")
            check_health
            get_connections
            get_database_size
            get_table_stats
            get_index_usage
            get_cache_hit_ratios
            get_autovacuum_info
            check_bloat
            generate_report
            ;;
        *)
            print_error "Invalid monitoring type: $MONITOR_TYPE"
            echo "Usage: $0 [health|connections|size|tables|indexes|slow|locks|cache|vacuum|bloat|report|all]"
            exit 1
            ;;
    esac
    
    print_status "Database monitoring completed"
}

# Run main function with all arguments
main "$@"