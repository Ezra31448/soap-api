#!/usr/bin/env python3
"""
Database Connection Test Script for Enhanced User Management System
This script tests the connection between the application and the database
"""
import os
import sys
import asyncio
import asyncpg
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
from datetime import datetime

# Add src to path to import settings
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.config.settings import settings
from src.database.connection import init_database, close_database, get_database_status, execute_query


class DatabaseTester:
    """Tests database connection and functionality"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "PASSED" if passed else "FAILED"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"[{status}] {test_name}")
        if message:
            print(f"    {message}")
    
    async def test_basic_connection(self) -> bool:
        """Test basic database connection"""
        try:
            # Test direct connection
            conn = await asyncpg.connect(self.db_url)
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            
            self.log_test("Basic Connection", True, f"Connected to PostgreSQL: {version[:50]}...")
            return True
        except Exception as e:
            self.log_test("Basic Connection", False, str(e))
            return False
    
    async def test_application_connection(self) -> bool:
        """Test application database connection"""
        try:
            # Initialize database connection through application
            await init_database()
            status = await get_database_status()
            
            if status["status"] == "healthy":
                self.log_test("Application Connection", True, 
                            f"Database version: {status.get('version', 'Unknown')}")
                return True
            else:
                self.log_test("Application Connection", False, 
                            f"Database status: {status.get('status', 'Unknown')}")
                return False
        except Exception as e:
            self.log_test("Application Connection", False, str(e))
            return False
    
    async def test_table_existence(self) -> bool:
        """Test if all required tables exist"""
        required_tables = [
            "users", "roles", "permissions", "user_roles", 
            "role_permissions", "audit_logs", "sessions"
        ]
        
        try:
            missing_tables = []
            for table in required_tables:
                result = await execute_query(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    {"table_name": table}
                )
                exists = result.scalar()
                
                if not exists:
                    missing_tables.append(table)
            
            if not missing_tables:
                self.log_test("Table Existence", True, 
                            f"All {len(required_tables)} required tables exist")
                return True
            else:
                self.log_test("Table Existence", False, 
                            f"Missing tables: {', '.join(missing_tables)}")
                return False
        except Exception as e:
            self.log_test("Table Existence", False, str(e))
            return False
    
    async def test_initial_data(self) -> bool:
        """Test if initial data is present"""
        try:
            # Check if roles exist
            roles_result = await execute_query("SELECT COUNT(*) FROM roles")
            roles_count = roles_result.scalar()
            
            # Check if permissions exist
            permissions_result = await execute_query("SELECT COUNT(*) FROM permissions")
            permissions_count = permissions_result.scalar()
            
            # Check if admin user exists
            admin_result = await execute_query(
                "SELECT COUNT(*) FROM users WHERE email = 'admin@example.com'"
            )
            admin_count = admin_result.scalar()
            
            if roles_count > 0 and permissions_count > 0 and admin_count > 0:
                self.log_test("Initial Data", True, 
                            f"Roles: {roles_count}, Permissions: {permissions_count}, Admin users: {admin_count}")
                return True
            else:
                self.log_test("Initial Data", False, 
                            f"Roles: {roles_count}, Permissions: {permissions_count}, Admin users: {admin_count}")
                return False
        except Exception as e:
            self.log_test("Initial Data", False, str(e))
            return False
    
    async def test_database_operations(self) -> bool:
        """Test basic database operations"""
        try:
            # Test INSERT
            await execute_query(
                "INSERT INTO users (email, password_hash, first_name, last_name, status) VALUES ($1, $2, $3, $4, $5)",
                {
                    "email": "test@example.com",
                    "password_hash": "test_hash",
                    "first_name": "Test",
                    "last_name": "User",
                    "status": "ACTIVE"
                }
            )
            
            # Test SELECT
            result = await execute_query(
                "SELECT id, email FROM users WHERE email = $1",
                {"email": "test@example.com"}
            )
            user = result.fetchone()
            
            if user:
                # Test UPDATE
                await execute_query(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1",
                    {"id": user["id"]}
                )
                
                # Test DELETE
                await execute_query(
                    "DELETE FROM users WHERE id = $1",
                    {"id": user["id"]}
                )
                
                self.log_test("Database Operations", True, 
                            "INSERT, SELECT, UPDATE, DELETE operations successful")
                return True
            else:
                self.log_test("Database Operations", False, "Failed to retrieve test user")
                return False
        except Exception as e:
            self.log_test("Database Operations", False, str(e))
            return False
    
    async def test_stored_procedures(self) -> bool:
        """Test stored procedures"""
        try:
            # Test cleanup_expired_sessions function
            result = await execute_query("SELECT cleanup_expired_sessions()")
            sessions_cleaned = result.scalar()
            
            # Test cleanup_old_audit_logs function
            result = await execute_query("SELECT cleanup_old_audit_logs()")
            logs_cleaned = result.scalar()
            
            self.log_test("Stored Procedures", True, 
                        f"Sessions cleaned: {sessions_cleaned}, Logs cleaned: {logs_cleaned}")
            return True
        except Exception as e:
            self.log_test("Stored Procedures", False, str(e))
            return False
    
    async def test_views(self) -> bool:
        """Test database views"""
        try:
            # Test user_roles_view
            result = await execute_query("SELECT COUNT(*) FROM user_roles_view LIMIT 1")
            user_roles_count = result.scalar()
            
            # Test user_permissions_view
            result = await execute_query("SELECT COUNT(*) FROM user_permissions_view LIMIT 1")
            user_permissions_count = result.scalar()
            
            self.log_test("Database Views", True, 
                        f"User roles view: {user_roles_count}, User permissions view: {user_permissions_count}")
            return True
        except Exception as e:
            self.log_test("Database Views", False, str(e))
            return False
    
    async def test_indexes(self) -> bool:
        """Test if important indexes exist"""
        important_indexes = [
            "idx_users_email", "idx_users_status", "idx_roles_name",
            "idx_permissions_module", "idx_permissions_action",
            "idx_user_roles_user_id", "idx_user_roles_role_id",
            "idx_role_permissions_role_id", "idx_role_permissions_permission_id"
        ]
        
        try:
            missing_indexes = []
            for index in important_indexes:
                result = await execute_query(
                    "SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = $1)",
                    {"indexname": index}
                )
                exists = result.scalar()
                
                if not exists:
                    missing_indexes.append(index)
            
            if not missing_indexes:
                self.log_test("Database Indexes", True, 
                            f"All {len(important_indexes)} important indexes exist")
                return True
            else:
                self.log_test("Database Indexes", False, 
                            f"Missing indexes: {', '.join(missing_indexes)}")
                return False
        except Exception as e:
            self.log_test("Database Indexes", False, str(e))
            return False
    
    async def test_connection_pooling(self) -> bool:
        """Test connection pooling"""
        try:
            # Create multiple concurrent connections
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    execute_query(f"SELECT {i} as test_id, pg_sleep(0.1)")
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            if len(results) == 5:
                self.log_test("Connection Pooling", True, 
                            "Successfully handled 5 concurrent connections")
                return True
            else:
                self.log_test("Connection Pooling", False, 
                            f"Expected 5 results, got {len(results)}")
                return False
        except Exception as e:
            self.log_test("Connection Pooling", False, str(e))
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all database tests"""
        print("Starting Database Connection Tests")
        print("=" * 50)
        
        # Run tests in order
        tests = [
            self.test_basic_connection,
            self.test_application_connection,
            self.test_table_existence,
            self.test_initial_data,
            self.test_database_operations,
            self.test_stored_procedures,
            self.test_views,
            self.test_indexes,
            self.test_connection_pooling
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
        
        # Close database connection
        await close_database()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASSED")
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "results": self.test_results
        }
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        if results['failed_tests'] > 0:
            print("\nFailed Tests:")
            print("-" * 30)
            for result in results['results']:
                if result['status'] == 'FAILED':
                    print(f"• {result['test']}: {result['message']}")
        
        # Overall result
        if results['success_rate'] == 100:
            print("\n✅ All tests passed! Database is ready for use.")
        elif results['success_rate'] >= 80:
            print("\n⚠️  Most tests passed. Database is mostly ready.")
        else:
            print("\n❌ Multiple tests failed. Database needs attention.")
    
    def save_report(self, results: Dict[str, Any], filename: Optional[str] = None):
        """Save test report to file"""
        if not filename:
            filename = f"database_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test report saved to: {filename}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database Connection Test Script")
    parser.add_argument("--save-report", action="store_true", 
                       help="Save test report to file")
    parser.add_argument("--report-file", type=str, 
                       help="Custom report file name")
    
    args = parser.parse_args()
    
    tester = DatabaseTester()
    results = await tester.run_all_tests()
    tester.print_summary(results)
    
    if args.save_report:
        tester.save_report(results, args.report_file)
    
    # Exit with appropriate code
    sys.exit(0 if results['success_rate'] == 100 else 1)


if __name__ == "__main__":
    asyncio.run(main())