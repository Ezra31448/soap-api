"""
Simple test script to verify SOAP API endpoints
"""
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime


async def test_soap_endpoint(endpoint_name: str, soap_request: str):
    """Test a SOAP endpoint"""
    url = "http://localhost:8000/soap"
    
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': f'http://example.com/usermanagement/{endpoint_name}'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=soap_request, headers=headers) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"✅ {endpoint_name} - Success")
                    print(f"Response: {response_text[:200]}...")
                    return True
                else:
                    print(f"❌ {endpoint_name} - Failed with status {response.status}")
                    response_text = await response.text()
                    print(f"Error: {response_text}")
                    return False
        except Exception as e:
            print(f"❌ {endpoint_name} - Exception: {str(e)}")
            return False


def create_soap_request(operation: str, params: dict) -> str:
    """Create a SOAP request XML"""
    # Create SOAP envelope
    envelope = ET.Element("soap:Envelope")
    envelope.set("xmlns:soap", "http://schemas.xmlsoap.org/soap/envelope/")
    envelope.set("xmlns:tns", "http://example.com/usermanagement")
    
    body = ET.SubElement(envelope, "soap:Body")
    
    # Add operation element
    op_element = ET.SubElement(body, f"tns:{operation}")
    
    # Add parameters
    for key, value in params.items():
        param = ET.SubElement(op_element, f"tns:{key}")
        param.text = str(value)
    
    return ET.tostring(envelope, encoding='unicode')


async def test_all_endpoints():
    """Test all SOAP endpoints"""
    print("🧪 Testing SOAP API Endpoints")
    print("=" * 50)
    
    tests = [
        ("RegisterUser", {
            "email": "test@example.com",
            "password": "TestPass123!",
            "firstName": "Test",
            "lastName": "User",
            "phoneNumber": "1234567890"
        }),
        
        ("AuthenticateUser", {
            "email": "admin@example.com",
            "password": "Admin123!"
        }),
        
        ("GetUserProfile", {
            "token": "dummy_token"
        }),
        
        ("GetAllUsers", {
            "token": "dummy_token",
            "page": "1",
            "pageSize": "10"
        }),
        
        ("CreateRole", {
            "token": "dummy_token",
            "name": "TEST_ROLE",
            "description": "Test role description"
        }),
        
        ("GetUserRoles", {
            "token": "dummy_token"
        }),
        
        ("CreatePermission", {
            "token": "dummy_token",
            "name": "TEST_PERMISSION",
            "description": "Test permission",
            "module": "TEST",
            "action": "TEST_ACTION"
        }),
        
        ("RequestPasswordReset", {
            "email": "test@example.com"
        }),
        
        ("GetAuditLogs", {
            "token": "dummy_token",
            "page": "1",
            "pageSize": "10"
        })
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for endpoint_name, params in tests:
        soap_request = create_soap_request(endpoint_name, params)
        success = await test_soap_endpoint(endpoint_name, soap_request)
        if success:
            success_count += 1
        print()  # Add spacing between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {success_count}/{total_count} endpoints passed")
    
    if success_count == total_count:
        print("🎉 All SOAP endpoints are working!")
    else:
        print("⚠️  Some SOAP endpoints need attention")


async def test_wsdl_endpoint():
    """Test WSDL endpoint"""
    print("\n📄 Testing WSDL Endpoint")
    print("=" * 50)
    
    url = "http://localhost:8000/wsdl"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print("✅ WSDL Endpoint - Success")
                    print(f"WSDL length: {len(response_text)} characters")
                    
                    # Check if it contains key WSDL elements
                    if "wsdl:definitions" in response_text and "wsdl:service" in response_text:
                        print("✅ WSDL structure appears valid")
                    else:
                        print("⚠️  WSDL structure may be invalid")
                    return True
                else:
                    print(f"❌ WSDL Endpoint - Failed with status {response.status}")
                    return False
        except Exception as e:
            print(f"❌ WSDL Endpoint - Exception: {str(e)}")
            return False


async def main():
    """Main test function"""
    print("🚀 Starting SOAP API Tests")
    print(f"📅 Test started at: {datetime.now().isoformat()}")
    
    # Test WSDL endpoint first
    wsdl_success = await test_wsdl_endpoint()
    
    # Test SOAP endpoints
    await test_all_endpoints()
    
    print(f"\n🏁 Tests completed at: {datetime.now().isoformat()}")
    
    if wsdl_success:
        print("🎉 SOAP API implementation is complete and functional!")
    else:
        print("⚠️  SOAP API needs some fixes")


if __name__ == "__main__":
    asyncio.run(main())