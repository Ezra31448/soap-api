#!/usr/bin/env python3
"""
Simple test script to verify the SOAP Wallet Service
"""

import requests
import xml.etree.ElementTree as ET

# SOAP endpoint
SOAP_URL = "http://localhost:8001/"

def test_register_wallet():
    """Test register_wallet SOAP method"""
    soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wallet="wallet.soap">
    <soap:Body>
        <wallet:register_wallet>
            <wallet:username>testuser123</wallet:username>
            <wallet:email>test@example.com</wallet:email>
        </wallet:register_wallet>
    </soap:Body>
</soap:Envelope>'''
    
    headers = {'Content-Type': 'text/xml'}
    response = requests.post(SOAP_URL, data=soap_request, headers=headers)
    
    print("=== Register Wallet Test ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.text}")
    
    # Parse response to extract wallet_uid
    try:
        root = ET.fromstring(response.text)
        wallet_uid_elem = root.find('.//{wallet.soap}wallet_uid')
        if wallet_uid_elem is not None:
            wallet_uid = wallet_uid_elem.text
            print(f"Wallet UID: {wallet_uid}")
            return wallet_uid
    except Exception as e:
        print(f"Error parsing response: {e}")
    
    return None

def test_get_balance(wallet_uid):
    """Test get_balance SOAP method"""
    soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wallet="wallet.soap">
    <soap:Body>
        <wallet:get_balance>
            <wallet:wallet_uid>{wallet_uid}</wallet:wallet_uid>
        </wallet:get_balance>
    </soap:Body>
</soap:Envelope>'''
    
    headers = {'Content-Type': 'text/xml'}
    response = requests.post(SOAP_URL, data=soap_request, headers=headers)
    
    print("\n=== Get Balance Test ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.text}")

def test_top_up(wallet_uid, amount=100.50):
    """Test top_up SOAP method"""
    soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wallet="wallet.soap">
    <soap:Body>
        <wallet:top_up>
            <wallet:wallet_uid>{wallet_uid}</wallet:wallet_uid>
            <wallet:amount>{amount}</wallet:amount>
        </wallet:top_up>
    </soap:Body>
</soap:Envelope>'''
    
    headers = {'Content-Type': 'text/xml'}
    response = requests.post(SOAP_URL, data=soap_request, headers=headers)
    
    print(f"\n=== Top Up Test (Amount: {amount}) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.text}")

def test_payment(wallet_uid, amount=50.25):
    """Test payment SOAP method"""
    soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:wallet="wallet.soap">
    <soap:Body>
        <wallet:payment>
            <wallet:wallet_uid>{wallet_uid}</wallet:wallet_uid>
            <wallet:amount>{amount}</wallet:amount>
        </wallet:payment>
    </soap:Body>
</soap:Envelope>'''
    
    headers = {'Content-Type': 'text/xml'}
    response = requests.post(SOAP_URL, data=soap_request, headers=headers)
    
    print(f"\n=== Payment Test (Amount: {amount}) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.text}")

if __name__ == '__main__':
    print("Testing SOAP Wallet Service...")
    
    # Test 1: Register a new wallet
    wallet_uid = test_register_wallet()
    
    if wallet_uid:
        # Test 2: Get initial balance (should be 0)
        test_get_balance(wallet_uid)
        
        # Test 3: Top up the wallet
        test_top_up(wallet_uid, 100.50)
        
        # Test 4: Get balance after top up
        test_get_balance(wallet_uid)
        
        # Test 5: Make a payment
        test_payment(wallet_uid, 50.25)
        
        # Test 6: Get final balance
        test_get_balance(wallet_uid)
        
        print(f"\n✅ All tests completed successfully!")
        print(f"Wallet UID used: {wallet_uid}")
    else:
        print("❌ Failed to register wallet")
