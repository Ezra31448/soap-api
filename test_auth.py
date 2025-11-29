#!/usr/bin/env python3
"""
Test script to verify authentication functionality
Tests: register, login, token verification, and protected endpoints
"""

import requests
from lxml import etree
import sys

SOAP_URL = "http://localhost:8000/soap"
HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

def create_soap_envelope(body_content):
    """Create a SOAP envelope with the given body content"""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:tns="spyne.examples.hello.soap">
    <soap:Body>
        {body_content}
    </soap:Body>
</soap:Envelope>"""

def create_soap_envelope_with_auth(body_content, token):
    """Create a SOAP envelope with Authorization header"""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:tns="spyne.examples.hello.soap">
    <soap:Header>
        <Authorization>Bearer {token}</Authorization>
    </soap:Header>
    <soap:Body>
        {body_content}
    </soap:Body>
</soap:Envelope>"""

def extract_text(xml_str, xpath):
    """Extract text from XML using XPath"""
    try:
        root = etree.fromstring(xml_str.encode())
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'tns': 'spyne.examples.hello.soap'
        }
        result = root.xpath(xpath, namespaces=namespaces)
        return result[0].text if result else None
    except:
        return None

def check_fault(xml_str):
    """Check if response contains SOAP fault"""
    try:
        root = etree.fromstring(xml_str.encode())
        namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/'}
        faults = root.xpath('//soap:Fault/faultstring/text()', namespaces=namespaces)
        return faults[0] if faults else None
    except:
        return None

def test_register(username, password):
    """Test user registration"""
    print(f"\n🧪 Testing Registration: username='{username}'")
    
    body = f"""
        <tns:register>
            <tns:username>{username}</tns:username>
            <tns:password>{password}</tns:password>
        </tns:register>
    """
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body), headers=HEADERS)
    
    fault = check_fault(response.text)
    if fault:
        print(f"   ❌ Registration failed: {fault}")
        return False
    
    result = extract_text(response.text, '//tns:registerResponse/tns:registerResult')
    if result and "SUCCESS" in result:
        print(f"   ✅ {result}")
        return True
    else:
        print(f"   ❌ Unexpected response")
        return False

def test_login(username, password):
    """Test user login and return token"""
    print(f"\n🔑 Testing Login: username='{username}'")
    
    body = f"""
        <tns:login>
            <tns:username>{username}</tns:username>
            <tns:password>{password}</tns:password>
        </tns:login>
    """
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body), headers=HEADERS)
    
    fault = check_fault(response.text)
    if fault:
        print(f"   ❌ Login failed: {fault}")
        return None
    
    token = extract_text(response.text, '//tns:loginResponse/tns:loginResult')
    if token:
        print(f"   ✅ Login successful! Token: {token[:50]}...")
        return token
    else:
        print(f"   ❌ No token received")
        return None

def test_verify_token(token):
    """Test token verification"""
    print(f"\n🔍 Testing Token Verification")
    
    body = f"""
        <tns:verify_token>
            <tns:token>{token}</tns:token>
        </tns:verify_token>
    """
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body), headers=HEADERS)
    
    fault = check_fault(response.text)
    if fault:
        print(f"   ❌ Verification failed: {fault}")
        return False
    
    result = extract_text(response.text, '//tns:verify_tokenResponse/tns:verify_tokenResult')
    if result:
        print(f"   ✅ {result}")
        return True
    else:
        print(f"   ❌ Unexpected response")
        return False

def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without authentication"""
    print(f"\n🚫 Testing Protected Endpoint WITHOUT Auth")
    
    body = """
        <tns:get_all_customers/>
    """
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body), headers=HEADERS)
    
    fault = check_fault(response.text)
    if fault and "Unauthorized" in fault:
        print(f"   ✅ Correctly rejected: {fault}")
        return True
    else:
        print(f"   ❌ Should have been rejected but wasn't")
        return False

def test_protected_endpoint_with_auth(token):
    """Test accessing protected endpoint with valid authentication"""
    print(f"\n✅ Testing Protected Endpoint WITH Valid Auth")
    
    # First create a customer to ensure we have data
    body_create = """
        <tns:create_customer>
            <tns:full_name>Test User</tns:full_name>
            <tns:email>test@example.com</tns:email>
            <tns:phone_number>123-456-7890</tns:phone_number>
        </tns:create_customer>
    """
    
    # Add Authorization to HTTP headers instead of SOAP header for better compatibility
    headers_with_auth = HEADERS.copy()
    headers_with_auth["Authorization"] = f"Bearer {token}"
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body_create), headers=headers_with_auth)
    
    fault = check_fault(response.text)
    if fault:
        print(f"   ⚠️  Create customer: {fault}")
    else:
        result = extract_text(response.text, '//tns:create_customerResponse/tns:create_customerResult')
        print(f"   📝 Create customer: {result}")
    
    # Now test get_all_customers
    body_get = """
        <tns:get_all_customers/>
    """
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body_get), headers=headers_with_auth)
    
    fault = check_fault(response.text)
    if fault:
        print(f"   ❌ Request failed: {fault}")
        return False
    
    # Check if we got customers back
    if "CustomerModel" in response.text or "get_all_customersResponse" in response.text:
        print(f"   ✅ Successfully accessed protected endpoint!")
        return True
    else:
        print(f"   ❌ Unexpected response")
        return False

def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    print(f"\n⛔ Testing Protected Endpoint WITH Invalid Token")
    
    body = """
        <tns:get_all_customers/>
    """
    
    headers_with_fake_auth = HEADERS.copy()
    headers_with_fake_auth["Authorization"] = "Bearer fake-invalid-token-12345"
    
    response = requests.post(SOAP_URL, data=create_soap_envelope(body), headers=headers_with_fake_auth)
    
    fault = check_fault(response.text)
    if fault and ("Unauthorized" in fault or "Invalid token" in fault):
        print(f"   ✅ Correctly rejected invalid token: {fault}")
        return True
    else:
        print(f"   ❌ Should have rejected invalid token")
        return False

def main():
    print("=" * 60)
    print("🔐 SOAP API Authentication Test Suite")
    print("=" * 60)
    
    test_username = "testuser"
    test_password = "testpass123"
    
    results = []
    
    # Test 1: Register new user
    results.append(("Register User", test_register(test_username, test_password)))
    
    # Test 2: Try to register duplicate user (should fail)
    results.append(("Duplicate Registration (should fail)", not test_register(test_username, test_password)))
    
    # Test 3: Login
    token = test_login(test_username, test_password)
    results.append(("User Login", token is not None))
    
    if token:
        # Test 4: Verify token
        results.append(("Verify Token", test_verify_token(token)))
        
        # Test 5: Access protected endpoint without auth
        results.append(("Protected Endpoint Without Auth", test_protected_endpoint_without_auth()))
        
        # Test 6: Access protected endpoint with invalid token
        results.append(("Protected Endpoint Invalid Token", test_protected_endpoint_with_invalid_token()))
        
        # Test 7: Access protected endpoint with valid auth
        results.append(("Protected Endpoint With Auth", test_protected_endpoint_with_auth(token)))
    
    # Test 8: Login with invalid credentials
    print(f"\n❌ Testing Login with Invalid Credentials")
    invalid_token = test_login("wronguser", "wrongpass")
    results.append(("Login Invalid Credentials (should fail)", invalid_token is None))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
