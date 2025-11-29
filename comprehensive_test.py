#!/usr/bin/env python3
"""
Comprehensive integration test script for SOAP API system
Tests all components: Docker services, database, Redis, SOAP endpoints, WSDL, etc.
"""
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import json
import time
import sys
import subprocess
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple


class SOAPAPITester:
    """Comprehensive SOAP API tester"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.soap_url = f"{base_url}/soap"
        self.wsdl_url = f"{base_url}/wsdl"
        self.health_url = f"{base_url}/health"
        self.test_results = []
        self.auth_token = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive SOAP API System Tests")
        print("=" * 60)
        
        # Test 1: Docker Services Status
        await self.test_docker_services()
        
        # Test 2: Health Checks
        await self.test_health_checks()
        
        # Test 3: Database Connection
        await self.test_database_connection()
        
        # Test 4: Redis Connection
        await self.test_redis_connection()
        
        # Test 5: WSDL Generation
        await self.test_wsdl_generation()
        
        # Test 6: Authentication Flow
        await self.test_authentication_flow()
        
        # Test 7: User Management
        await self.test_user_management()
        
        # Test 8: Role Management
        await self.test_role_management()
        
        # Test 9: Error Handling
        await self.test_error_handling()
        
        # Test 10: Audit Logging
        await self.test_audit_logging()
        
        # Generate final report
        return self.generate_test_report()
    
    async def test_docker_services(self) -> None:
        """Test Docker services status"""
        print("\n🐳 Testing Docker Services Status")
        print("-" * 40)
        
        try:
            # Check if Docker is running
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode != 0:
                self.add_test_result("Docker Daemon", False, "Docker daemon is not running")
                return
            
            # Check running containers
            containers = result.stdout
            services = ['soap-api-postgres', 'soap-api-redis', 'soap-api-service']
            
            for service in services:
                if service in containers:
                    self.add_test_result(f"Docker Service: {service}", True, "Container is running")
                else:
                    self.add_test_result(f"Docker Service: {service}", False, "Container is not running")
                    
        except Exception as e:
            self.add_test_result("Docker Services", False, f"Error checking Docker: {str(e)}")
    
    async def test_health_checks(self) -> None:
        """Test health check endpoints"""
        print("\n🏥 Testing Health Check Endpoints")
        print("-" * 40)
        
        endpoints = [
            ("/health", "Basic Health Check"),
            ("/health/ready", "Readiness Check"),
            ("/health/live", "Liveness Check"),
            ("/health/detailed", "Detailed Health Check")
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint, description in endpoints:
                try:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            data = await response.json()
                            self.add_test_result(description, True, f"Status: {response.status}")
                            print(f"  ✅ {description}: {data.get('status', 'unknown')}")
                        else:
                            self.add_test_result(description, False, f"Status: {response.status}")
                            print(f"  ❌ {description}: HTTP {response.status}")
                except Exception as e:
                    self.add_test_result(description, False, f"Connection error: {str(e)}")
                    print(f"  ❌ {description}: {str(e)}")
    
    async def test_database_connection(self) -> None:
        """Test database connection"""
        print("\n🗄️ Testing Database Connection")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.health_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        db_status = data.get('checks', {}).get('database', {})
                        
                        if db_status.get('status') == 'healthy':
                            self.add_test_result("Database Connection", True, "Database is healthy")
                            print(f"  ✅ Database: {db_status.get('version', 'unknown version')}")
                        else:
                            self.add_test_result("Database Connection", False, 
                                               f"Database unhealthy: {db_status.get('error', 'unknown error')}")
                            print(f"  ❌ Database: {db_status.get('error', 'unknown error')}")
                    else:
                        self.add_test_result("Database Connection", False, f"Health check failed: {response.status}")
        except Exception as e:
            self.add_test_result("Database Connection", False, f"Connection error: {str(e)}")
            print(f"  ❌ Database: {str(e)}")
    
    async def test_redis_connection(self) -> None:
        """Test Redis connection"""
        print("\n🔴 Testing Redis Connection")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.health_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        redis_status = data.get('checks', {}).get('redis', {})
                        
                        if redis_status.get('status') == 'healthy':
                            self.add_test_result("Redis Connection", True, "Redis is healthy")
                            print(f"  ✅ Redis: Version {redis_status.get('version', 'unknown')}")
                        else:
                            self.add_test_result("Redis Connection", False, 
                                               f"Redis unhealthy: {redis_status.get('error', 'unknown error')}")
                            print(f"  ❌ Redis: {redis_status.get('error', 'unknown error')}")
                    else:
                        self.add_test_result("Redis Connection", False, f"Health check failed: {response.status}")
        except Exception as e:
            self.add_test_result("Redis Connection", False, f"Connection error: {str(e)}")
            print(f"  ❌ Redis: {str(e)}")
    
    async def test_wsdl_generation(self) -> None:
        """Test WSDL generation and accessibility"""
        print("\n📄 Testing WSDL Generation")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.wsdl_url) as response:
                    if response.status == 200:
                        wsdl_content = await response.text()
                        
                        # Check WSDL structure
                        required_elements = [
                            'wsdl:definitions',
                            'wsdl:types',
                            'wsdl:message',
                            'wsdl:portType',
                            'wsdl:binding',
                            'wsdl:service'
                        ]
                        
                        missing_elements = []
                        for element in required_elements:
                            if element not in wsdl_content:
                                missing_elements.append(element)
                        
                        if not missing_elements:
                            self.add_test_result("WSDL Generation", True, "WSDL structure is valid")
                            print(f"  ✅ WSDL: Generated successfully ({len(wsdl_content)} characters)")
                        else:
                            self.add_test_result("WSDL Generation", False, 
                                               f"Missing elements: {', '.join(missing_elements)}")
                            print(f"  ❌ WSDL: Missing elements: {', '.join(missing_elements)}")
                    else:
                        self.add_test_result("WSDL Generation", False, f"HTTP {response.status}")
                        print(f"  ❌ WSDL: HTTP {response.status}")
        except Exception as e:
            self.add_test_result("WSDL Generation", False, f"Error: {str(e)}")
            print(f"  ❌ WSDL: {str(e)}")
    
    async def test_authentication_flow(self) -> None:
        """Test authentication flow"""
        print("\n🔐 Testing Authentication Flow")
        print("-" * 40)
        
        # Test 1: Register new user
        register_result = await self.soap_request("RegisterUser", {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "firstName": "Test",
            "lastName": "User",
            "phoneNumber": "1234567890"
        })
        
        if register_result['success']:
            self.add_test_result("User Registration", True, "User registered successfully")
            print("  ✅ Registration: User created successfully")
        else:
            self.add_test_result("User Registration", False, register_result.get('error', 'Unknown error'))
            print(f"  ❌ Registration: {register_result.get('error', 'Unknown error')}")
        
        # Test 2: Authenticate user
        auth_result = await self.soap_request("AuthenticateUser", {
            "email": "admin@example.com",  # Assuming admin user exists
            "password": "Admin123!"
        })
        
        if auth_result['success'] and 'token' in auth_result.get('data', {}):
            self.auth_token = auth_result['data']['token']
            self.add_test_result("User Authentication", True, "User authenticated successfully")
            print("  ✅ Authentication: Login successful")
        else:
            self.add_test_result("User Authentication", False, auth_result.get('error', 'Authentication failed'))
            print(f"  ❌ Authentication: {auth_result.get('error', 'Authentication failed')}")
        
        # Test 3: Validate token
        if self.auth_token:
            profile_result = await self.soap_request("GetUserProfile", {
                "token": self.auth_token
            })
            
            if profile_result['success']:
                self.add_test_result("Token Validation", True, "Token is valid")
                print("  ✅ Token Validation: Token is valid")
            else:
                self.add_test_result("Token Validation", False, profile_result.get('error', 'Token validation failed'))
                print(f"  ❌ Token Validation: {profile_result.get('error', 'Token validation failed')}")
    
    async def test_user_management(self) -> None:
        """Test user management operations"""
        print("\n👥 Testing User Management")
        print("-" * 40)
        
        if not self.auth_token:
            self.add_test_result("User Management", False, "No authentication token available")
            print("  ❌ User Management: No authentication token")
            return
        
        # Test 1: Get all users
        users_result = await self.soap_request("GetAllUsers", {
            "token": self.auth_token,
            "page": 1,
            "pageSize": 10
        })
        
        if users_result['success']:
            self.add_test_result("Get All Users", True, "Users retrieved successfully")
            print(f"  ✅ Get Users: Retrieved users successfully")
        else:
            self.add_test_result("Get All Users", False, users_result.get('error', 'Failed to get users'))
            print(f"  ❌ Get Users: {users_result.get('error', 'Failed to get users')}")
        
        # Test 2: Update user profile
        update_result = await self.soap_request("UpdateUserProfile", {
            "token": self.auth_token,
            "firstName": "Updated",
            "lastName": "Name"
        })
        
        if update_result['success']:
            self.add_test_result("Update Profile", True, "Profile updated successfully")
            print("  ✅ Update Profile: Profile updated successfully")
        else:
            self.add_test_result("Update Profile", False, update_result.get('error', 'Failed to update profile'))
            print(f"  ❌ Update Profile: {update_result.get('error', 'Failed to update profile')}")
    
    async def test_role_management(self) -> None:
        """Test role management operations"""
        print("\n🔑 Testing Role Management")
        print("-" * 40)
        
        if not self.auth_token:
            self.add_test_result("Role Management", False, "No authentication token available")
            print("  ❌ Role Management: No authentication token")
            return
        
        # Test 1: Create role
        create_role_result = await self.soap_request("CreateRole", {
            "token": self.auth_token,
            "name": "TEST_ROLE",
            "description": "Test role for integration testing"
        })
        
        if create_role_result['success']:
            self.add_test_result("Create Role", True, "Role created successfully")
            print("  ✅ Create Role: Role created successfully")
        else:
            self.add_test_result("Create Role", False, create_role_result.get('error', 'Failed to create role'))
            print(f"  ❌ Create Role: {create_role_result.get('error', 'Failed to create role')}")
        
        # Test 2: Get user roles
        roles_result = await self.soap_request("GetUserRoles", {
            "token": self.auth_token
        })
        
        if roles_result['success']:
            self.add_test_result("Get User Roles", True, "User roles retrieved successfully")
            print("  ✅ Get Roles: User roles retrieved successfully")
        else:
            self.add_test_result("Get User Roles", False, roles_result.get('error', 'Failed to get user roles'))
            print(f"  ❌ Get Roles: {roles_result.get('error', 'Failed to get user roles')}")
    
    async def test_error_handling(self) -> None:
        """Test error handling and validation"""
        print("\n⚠️ Testing Error Handling")
        print("-" * 40)
        
        # Test 1: Invalid authentication
        invalid_auth = await self.soap_request("AuthenticateUser", {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        if not invalid_auth['success']:
            self.add_test_result("Invalid Auth Handling", True, "Invalid credentials properly rejected")
            print("  ✅ Invalid Auth: Invalid credentials properly rejected")
        else:
            self.add_test_result("Invalid Auth Handling", False, "Invalid credentials were accepted")
            print("  ❌ Invalid Auth: Invalid credentials were accepted")
        
        # Test 2: Invalid token
        invalid_token = await self.soap_request("GetUserProfile", {
            "token": "invalid_token_here"
        })
        
        if not invalid_token['success']:
            self.add_test_result("Invalid Token Handling", True, "Invalid token properly rejected")
            print("  ✅ Invalid Token: Invalid token properly rejected")
        else:
            self.add_test_result("Invalid Token Handling", False, "Invalid token was accepted")
            print("  ❌ Invalid Token: Invalid token was accepted")
        
        # Test 3: Missing required fields
        missing_fields = await self.soap_request("RegisterUser", {
            "email": "test@example.com"
            # Missing required fields
        })
        
        if not missing_fields['success']:
            self.add_test_result("Validation Handling", True, "Missing required fields properly rejected")
            print("  ✅ Validation: Missing required fields properly rejected")
        else:
            self.add_test_result("Validation Handling", False, "Missing required fields were accepted")
            print("  ❌ Validation: Missing required fields were accepted")
    
    async def test_audit_logging(self) -> None:
        """Test audit logging functionality"""
        print("\n📋 Testing Audit Logging")
        print("-" * 40)
        
        if not self.auth_token:
            self.add_test_result("Audit Logging", False, "No authentication token available")
            print("  ❌ Audit Logging: No authentication token")
            return
        
        # Test 1: Get audit logs
        audit_result = await self.soap_request("GetAuditLogs", {
            "token": self.auth_token,
            "page": 1,
            "pageSize": 10
        })
        
        if audit_result['success']:
            self.add_test_result("Get Audit Logs", True, "Audit logs retrieved successfully")
            print("  ✅ Audit Logs: Retrieved successfully")
        else:
            self.add_test_result("Get Audit Logs", False, audit_result.get('error', 'Failed to get audit logs'))
            print(f"  ❌ Audit Logs: {audit_result.get('error', 'Failed to get audit logs')}")
        
        # Test 2: Get user audit logs
        user_audit_result = await self.soap_request("GetUserAuditLogs", {
            "token": self.auth_token,
            "page": 1,
            "pageSize": 10
        })
        
        if user_audit_result['success']:
            self.add_test_result("Get User Audit Logs", True, "User audit logs retrieved successfully")
            print("  ✅ User Audit Logs: Retrieved successfully")
        else:
            self.add_test_result("Get User Audit Logs", False, user_audit_result.get('error', 'Failed to get user audit logs'))
            print(f"  ❌ User Audit Logs: {user_audit_result.get('error', 'Failed to get user audit logs')}")
    
    async def soap_request(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a SOAP request"""
        try:
            soap_envelope = self.create_soap_request(operation, params)
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': f'http://example.com/usermanagement/{operation}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.soap_url, data=soap_envelope, headers=headers) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        # Parse SOAP response
                        try:
                            root = ET.fromstring(response_text)
                            # Simple success check - look for success indicator
                            success_elements = root.findall('.//success')
                            if success_elements and success_elements[0].text.lower() == 'true':
                                return {'success': True, 'data': response_text}
                            else:
                                return {'success': False, 'error': 'SOAP response indicates failure'}
                        except ET.ParseError:
                            return {'success': False, 'error': 'Invalid SOAP response format'}
                    else:
                        return {'success': False, 'error': f'HTTP {response.status}: {response_text}'}
                        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_soap_request(self, operation: str, params: Dict[str, Any]) -> str:
        """Create SOAP request XML"""
        envelope = ET.Element("soap:Envelope")
        envelope.set("xmlns:soap", "http://schemas.xmlsoap.org/soap/envelope/")
        envelope.set("xmlns:tns", "http://example.com/usermanagement")
        
        body = ET.SubElement(envelope, "soap:Body")
        op_element = ET.SubElement(body, f"tns:{operation}")
        
        for key, value in params.items():
            param = ET.SubElement(op_element, f"tns:{key}")
            param.text = str(value)
        
        return ET.tostring(envelope, encoding='unicode')
    
    def add_test_result(self, test_name: str, success: bool, message: str) -> None:
        """Add test result to results list"""
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test_name']}: {result['message']}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests/total_tests*100,
            'test_results': self.test_results,
            'timestamp': datetime.utcnow().isoformat()
        }


async def main():
    """Main test function"""
    print("🧪 SOAP API Comprehensive Integration Test Suite")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    
    # Create tester instance
    tester = SOAPAPITester()
    
    # Run all tests
    results = await tester.run_all_tests()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Test results saved to: test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if results['failed_tests'] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())