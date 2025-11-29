#!/usr/bin/env python3
"""
Test script for SOAP API Authentication
"""

import requests
import xml.etree.ElementTree as ET
from decimal import Decimal

# SOAP API endpoint
BASE_URL = "http://localhost:8000"

# SOAP Namespaces
SOAP_NS = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'wallet': 'wallet.soap'
}

def create_soap_request(method_name, parameters, token=None):
    """Create a SOAP request with optional authentication token"""
    envelope = ET.Element('soap:Envelope', {
        'xmlns:soap': SOAP_NS['soap'],
        'xmlns:wallet': SOAP_NS['wallet']
    })
    
    # Add header with token if provided
    if token:
        header = ET.SubElement(envelope, 'soap:Header')
        token_element = ET.SubElement(header, 'wallet:token')
        token_element.text = token
    
    body = ET.SubElement(envelope, 'soap:Body')
    method = ET.SubElement(body, f'wallet:{method_name}')
    
    for key, value in parameters.items():
        param = ET.SubElement(method, f'wallet:{key}')
        param.text = str(value)
    
    return ET.tostring(envelope, encoding='unicode', method='xml')

def parse_soap_response(response_text):
    """Parse SOAP response and extract data"""
    try:
        root = ET.fromstring(response_text)
        body = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
        if body is None:
            return None, "No body in response"
        
        # Find the first child element (the response)
        response_element = None
        for child in body:
            response_element = child
            break
        
        if response_element is None:
            return None, "No response element found"
        
        # Extract response data
        response_data = {}
        for element in response_element:
            tag = element.tag.split('}')[-1]  # Remove namespace
            response_data[tag] = element.text
        
        return response_data, None
        
    except Exception as e:
        return None, f"Error parsing response: {str(e)}"

def test_authentication():
    """Test authentication flow"""
    print("=== Testing SOAP API Authentication ===")
    
    # Test data
    test_username = "testuser123"
    test_email = "testuser123@example.com"
    test_password = "securepassword123"
    
    # 1. Test user registration
    print("\n1. Testing user registration...")
    register_request = create_soap_request('register_user', {
        'username': test_username,
        'email': test_email,
        'password': test_password
    })
    
    response = requests.post(BASE_URL, data=register_request, headers={'Content-Type': 'text/xml'})
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Registration successful: {data}")
            user_id = data.get('user_id')
    else:
        print(f"Registration failed: {response.text}")
        return
    
    # 2. Test user login
    print("\n2. Testing user login...")
    login_request = create_soap_request('login_user', {
        'username': test_username,
        'password': test_password
    })
    
    response = requests.post(BASE_URL, data=login_request, headers={'Content-Type': 'text/xml'})
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Login successful: {data}")
            auth_token = data.get('token')
            print(f"Auth Token: {auth_token[:50]}...")
    else:
        print(f"Login failed: {response.text}")
        return
    
    # 3. Test wallet operations with authentication
    print("\n3. Testing wallet operations with authentication...")
    
    # Register wallet (requires auth)
    wallet_request = create_soap_request('register_wallet', {
        'username': test_username,
        'email': test_email
    }, token=auth_token)
    
    response = requests.post(BASE_URL, data=wallet_request, headers={'Content-Type': 'text/xml'})
    print(f"Wallet Registration Status: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Wallet registration successful: {data}")
            wallet_uid = data.get('wallet_uid')
    else:
        print(f"Wallet registration failed: {response.text}")
        return
    
    # 4. Test top-up operation
    print("\n4. Testing top-up operation...")
    top_up_request = create_soap_request('top_up', {
        'wallet_uid': wallet_uid,
        'amount': '100.50'
    }, token=auth_token)
    
    response = requests.post(BASE_URL, data=top_up_request, headers={'Content-Type': 'text/xml'})
    print(f"Top-up Status: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Top-up successful: {data}")
    
    # 5. Test get balance
    print("\n5. Testing get balance...")
    balance_request = create_soap_request('get_balance', {
        'wallet_uid': wallet_uid
    }, token=auth_token)
    
    response = requests.post(BASE_URL, data=balance_request, headers={'Content-Type': 'text/xml'})
    print(f"Get Balance Status: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Balance: {data}")
    
    # 6. Test payment operation
    print("\n6. Testing payment operation...")
    payment_request = create_soap_request('payment', {
        'wallet_uid': wallet_uid,
        'amount': '50.25'
    }, token=auth_token)
    
    response = requests.post(BASE_URL, data=payment_request, headers={'Content-Type': 'text/xml'})
    print(f"Payment Status: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Payment successful: {data}")
    
    # 7. Test logout
    print("\n7. Testing logout...")
    logout_request = create_soap_request('logout_user', {
        'token': auth_token
    })
    
    response = requests.post(BASE_URL, data=logout_request, headers={'Content-Type': 'text/xml'})
    print(f"Logout Status: {response.status_code}")
    
    if response.status_code == 200:
        data, error = parse_soap_response(response.text)
        if error:
            print(f"Error: {error}")
        else:
            print(f"Logout successful: {data}")
    
    # 8. Test accessing protected endpoint with invalid token
    print("\n8. Testing access with invalid token...")
    invalid_request = create_soap_request('get_balance', {
        'wallet_uid': wallet_uid
    }, token="invalid_token")
    
    response = requests.post(BASE_URL, data=invalid_request, headers={'Content-Type': 'text/xml'})
    print(f"Invalid Token Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    print("\n=== Authentication Test Complete ===")

if __name__ == '__main__':
    test_authentication()
