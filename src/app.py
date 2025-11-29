#!/usr/bin/env python3
"""
SOAP API Wallet Service using Flask and custom SOAP implementation
"""

import os
import logging
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from xml.etree import ElementTree as ET

from flask import Flask, request, Response
from sqlalchemy import create_engine, Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from auth import AuthService, User, TokenBlacklist
from model import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'wallet_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models from model.py
from model import Wallet, Transaction

# Create tables
Base.metadata.create_all(bind=engine)

# Flask application
app = Flask(__name__)

# SOAP Namespaces
SOAP_NS = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'wallet': 'wallet.soap'
}

# SOAP Response Templates
def create_soap_response(body_content):
    """Create a SOAP envelope response"""
    envelope = ET.Element('soap:Envelope', {
        'xmlns:soap': SOAP_NS['soap'],
        'xmlns:wallet': SOAP_NS['wallet']
    })
    body = ET.SubElement(envelope, 'soap:Body')
    body.append(body_content)
    return ET.tostring(envelope, encoding='unicode', method='xml')

def create_soap_fault(fault_code, fault_string):
    """Create a SOAP fault response"""
    envelope = ET.Element('soap:Envelope', {
        'xmlns:soap': SOAP_NS['soap']
    })
    body = ET.SubElement(envelope, 'soap:Body')
    fault = ET.SubElement(body, 'soap:Fault')
    faultcode = ET.SubElement(fault, 'faultcode')
    faultcode.text = f"wallet:{fault_code}"
    faultstring = ET.SubElement(fault, 'faultstring')
    faultstring.text = fault_string
    return ET.tostring(envelope, encoding='unicode', method='xml')

# SOAP Service Implementation
class WalletService:
    def register_wallet(self, username, email):
        """Register a new wallet for a user"""
        try:
            db = SessionLocal()
            
            # Check if username or email already exists
            existing_wallet = db.query(Wallet).filter(
                (Wallet.username == username) | (Wallet.email == email)
            ).first()
            
            if existing_wallet:
                return create_soap_fault("DUPLICATE_USER", "Username or email already exists")
            
            # Create new wallet
            wallet = Wallet(
                username=username,
                email=email
            )
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
            
            logger.info(f"Wallet created: {wallet.wallet_uid} for user {username}")
            
            # Create response
            response = ET.Element('wallet:register_walletResponse')
            wallet_uid = ET.SubElement(response, 'wallet:wallet_uid')
            wallet_uid.text = wallet.wallet_uid
            
            return create_soap_response(response)
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in register_wallet: {str(e)}")
            return create_soap_fault("DATABASE_ERROR", "Internal server error")
        finally:
            db.close()

    def top_up(self, wallet_uid, amount):
        """Add funds to wallet"""
        try:
            db = SessionLocal()
            
            wallet = db.query(Wallet).filter(Wallet.wallet_uid == wallet_uid).first()
            if not wallet:
                return create_soap_fault("WALLET_NOT_FOUND", "Wallet not found")
            
            if amount <= 0:
                return create_soap_fault("INVALID_AMOUNT", "Amount must be positive")
            
            # Update balance
            wallet.balance += Decimal(str(amount))
            wallet.updated_at = datetime.utcnow()
            
            # Create transaction record
            transaction = Transaction(
                wallet_uid=wallet.wallet_uid,
                amount=amount,
                transaction_type='top_up',
                description=f"Top up: {amount}"
            )
            db.add(transaction)
            
            db.commit()
            db.refresh(wallet)
            
            logger.info(f"Top up successful: {amount} added to wallet {wallet_uid}")
            
            # Create response
            response = ET.Element('wallet:top_upResponse')
            message = ET.SubElement(response, 'wallet:message')
            message.text = "Top up successful"
            new_balance = ET.SubElement(response, 'wallet:new_balance')
            new_balance.text = str(wallet.balance)
            
            return create_soap_response(response)
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in top_up: {str(e)}")
            return create_soap_fault("DATABASE_ERROR", "Internal server error")
        finally:
            db.close()

    def payment(self, wallet_uid, amount):
        """Deduct funds from wallet"""
        try:
            db = SessionLocal()
            
            wallet = db.query(Wallet).filter(Wallet.wallet_uid == wallet_uid).first()
            if not wallet:
                return create_soap_fault("WALLET_NOT_FOUND", "Wallet not found")
            
            if amount <= 0:
                return create_soap_fault("INVALID_AMOUNT", "Amount must be positive")
            
            if wallet.balance < amount:
                return create_soap_fault("INSUFFICIENT_BALANCE", "Insufficient balance")
            
            # Update balance
            wallet.balance -= Decimal(str(amount))
            wallet.updated_at = datetime.utcnow()
            
            # Create transaction record
            transaction = Transaction(
                wallet_uid=wallet.wallet_uid,
                amount=amount,
                transaction_type='payment',
                description=f"Payment: {amount}"
            )
            db.add(transaction)
            
            db.commit()
            db.refresh(wallet)
            
            logger.info(f"Payment successful: {amount} deducted from wallet {wallet_uid}")
            
            # Create response
            response = ET.Element('wallet:paymentResponse')
            message = ET.SubElement(response, 'wallet:message')
            message.text = "Payment successful"
            remaining_balance = ET.SubElement(response, 'wallet:remaining_balance')
            remaining_balance.text = str(wallet.balance)
            
            return create_soap_response(response)
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in payment: {str(e)}")
            return create_soap_fault("DATABASE_ERROR", "Internal server error")
        finally:
            db.close()

    def get_balance(self, wallet_uid):
        """Get current wallet balance"""
        try:
            db = SessionLocal()
            
            wallet = db.query(Wallet).filter(Wallet.wallet_uid == wallet_uid).first()
            if not wallet:
                return create_soap_fault("WALLET_NOT_FOUND", "Wallet not found")
            
            # Create response
            response = ET.Element('wallet:get_balanceResponse')
            balance = ET.SubElement(response, 'wallet:balance')
            balance.text = str(wallet.balance)
            
            return create_soap_response(response)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_balance: {str(e)}")
            return create_soap_fault("DATABASE_ERROR", "Internal server error")
        finally:
            db.close()

# Create service instances
wallet_service = WalletService()

# Authentication Service Implementation
class AuthSOAPService:
    def __init__(self):
        self.auth_service = None
    
    def get_auth_service(self):
        """Get auth service instance with database session"""
        if self.auth_service is None:
            db = SessionLocal()
            self.auth_service = AuthService(db)
        return self.auth_service
    
    def register_user(self, username, email, password):
        """Register a new user"""
        try:
            auth_service = self.get_auth_service()
            user, error = auth_service.create_user(username, email, password)
            
            if error:
                return create_soap_fault("REGISTRATION_ERROR", error)
            
            # Create response
            response = ET.Element('wallet:register_userResponse')
            user_id = ET.SubElement(response, 'wallet:user_id')
            user_id.text = user.id
            message = ET.SubElement(response, 'wallet:message')
            message.text = "User registered successfully"
            
            return create_soap_response(response)
            
        except Exception as e:
            logger.error(f"Error in register_user: {str(e)}")
            return create_soap_fault("INTERNAL_ERROR", "Internal server error")
    
    def login_user(self, username, password):
        """Authenticate user and return token"""
        try:
            auth_service = self.get_auth_service()
            user, error = auth_service.authenticate_user(username, password)
            
            if error:
                return create_soap_fault("AUTHENTICATION_ERROR", error)
            
            token = auth_service.generate_token(user)
            
            # Create response
            response = ET.Element('wallet:login_userResponse')
            token_element = ET.SubElement(response, 'wallet:token')
            token_element.text = token
            user_id = ET.SubElement(response, 'wallet:user_id')
            user_id.text = user.id
            username_element = ET.SubElement(response, 'wallet:username')
            username_element.text = user.username
            
            return create_soap_response(response)
            
        except Exception as e:
            logger.error(f"Error in login_user: {str(e)}")
            return create_soap_fault("INTERNAL_ERROR", "Internal server error")
    
    def logout_user(self, token):
        """Revoke user token"""
        try:
            auth_service = self.get_auth_service()
            success, error = auth_service.revoke_token(token)
            
            if not success:
                return create_soap_fault("LOGOUT_ERROR", error)
            
            # Create response
            response = ET.Element('wallet:logout_userResponse')
            message = ET.SubElement(response, 'wallet:message')
            message.text = "User logged out successfully"
            
            return create_soap_response(response)
            
        except Exception as e:
            logger.error(f"Error in logout_user: {str(e)}")
            return create_soap_fault("INTERNAL_ERROR", "Internal server error")

# Create auth service instance
auth_soap_service = AuthSOAPService()

def extract_token_from_soap_header(soap_request):
    """Extract JWT token from SOAP header"""
    try:
        header = soap_request.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Header')
        if header is not None:
            token_element = header.find('.//wallet:token', SOAP_NS)
            if token_element is not None:
                return token_element.text
        return None
    except Exception:
        return None

def authenticate_request(soap_request):
    """Authenticate SOAP request using JWT token"""
    token = extract_token_from_soap_header(soap_request)
    if not token:
        return None, "No authentication token provided"
    
    auth_service = auth_soap_service.get_auth_service()
    user, error = auth_service.verify_token(token)
    if error:
        return None, error
    
    return user, None

# SOAP Endpoint
@app.route('/', methods=['POST'])
def soap_endpoint():
    """Handle SOAP requests"""
    try:
        # Parse SOAP request
        soap_request = ET.fromstring(request.data)
        
        # Extract method name and parameters
        body = soap_request.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
        if body is None:
            return create_soap_fault("INVALID_REQUEST", "Invalid SOAP request")
        
        # Find the first child element (the method call)
        method_element = None
        for child in body:
            method_element = child
            break
        
        if method_element is None:
            return create_soap_fault("INVALID_REQUEST", "No method specified")
        
        method_name = method_element.tag.split('}')[-1]  # Remove namespace
        
        # Handle authentication methods (no auth required)
        if method_name == 'register_user':
            username = method_element.find('.//wallet:username', SOAP_NS).text
            email = method_element.find('.//wallet:email', SOAP_NS).text
            password = method_element.find('.//wallet:password', SOAP_NS).text
            response = auth_soap_service.register_user(username, email, password)
            
        elif method_name == 'login_user':
            username = method_element.find('.//wallet:username', SOAP_NS).text
            password = method_element.find('.//wallet:password', SOAP_NS).text
            response = auth_soap_service.login_user(username, password)
            
        elif method_name == 'logout_user':
            token = method_element.find('.//wallet:token', SOAP_NS).text
            response = auth_soap_service.logout_user(token)
            
        # Handle wallet methods (require authentication)
        elif method_name in ['register_wallet', 'top_up', 'payment', 'get_balance']:
            # Authenticate request
            user, auth_error = authenticate_request(soap_request)
            if auth_error:
                return create_soap_fault("AUTHENTICATION_ERROR", auth_error)
            
            if method_name == 'register_wallet':
                username = method_element.find('.//wallet:username', SOAP_NS).text
                email = method_element.find('.//wallet:email', SOAP_NS).text
                response = wallet_service.register_wallet(username, email)
                
            elif method_name == 'top_up':
                wallet_uid = method_element.find('.//wallet:wallet_uid', SOAP_NS).text
                amount = Decimal(method_element.find('.//wallet:amount', SOAP_NS).text)
                response = wallet_service.top_up(wallet_uid, amount)
                
            elif method_name == 'payment':
                wallet_uid = method_element.find('.//wallet:wallet_uid', SOAP_NS).text
                amount = Decimal(method_element.find('.//wallet:amount', SOAP_NS).text)
                response = wallet_service.payment(wallet_uid, amount)
                
            elif method_name == 'get_balance':
                wallet_uid = method_element.find('.//wallet:wallet_uid', SOAP_NS).text
                response = wallet_service.get_balance(wallet_uid)
            
        else:
            return create_soap_fault("METHOD_NOT_FOUND", f"Method {method_name} not found")
        
        return Response(response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error processing SOAP request: {str(e)}")
        return create_soap_fault("INTERNAL_ERROR", "Internal server error")

# WSDL Endpoint
@app.route('/', methods=['GET'])
def wsdl_endpoint():
    """Return WSDL definition"""
    wsdl = f'''<?xml version="1.0" encoding="UTF-8"?>
<definitions name="WalletService"
    targetNamespace="{SOAP_NS['wallet']}"
    xmlns:tns="{SOAP_NS['wallet']}"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns="http://schemas.xmlsoap.org/wsdl/">
    
    <types>
        <xsd:schema targetNamespace="{SOAP_NS['wallet']}">
            <!-- Authentication Operations -->
            <xsd:element name="register_user">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="username" type="xsd:string"/>
                        <xsd:element name="email" type="xsd:string"/>
                        <xsd:element name="password" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="register_userResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="user_id" type="xsd:string"/>
                        <xsd:element name="message" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <xsd:element name="login_user">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="username" type="xsd:string"/>
                        <xsd:element name="password" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="login_userResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="token" type="xsd:string"/>
                        <xsd:element name="user_id" type="xsd:string"/>
                        <xsd:element name="username" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <xsd:element name="logout_user">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="token" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="logout_userResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="message" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <!-- Register Wallet -->
            <xsd:element name="register_wallet">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="username" type="xsd:string"/>
                        <xsd:element name="email" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="register_walletResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="wallet_uid" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <!-- Top Up -->
            <xsd:element name="top_up">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="wallet_uid" type="xsd:string"/>
                        <xsd:element name="amount" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="top_upResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="message" type="xsd:string"/>
                        <xsd:element name="new_balance" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <!-- Payment -->
            <xsd:element name="payment">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="wallet_uid" type="xsd:string"/>
                        <xsd:element name="amount" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="paymentResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="message" type="xsd:string"/>
                        <xsd:element name="remaining_balance" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <!-- Get Balance -->
            <xsd:element name="get_balance">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="wallet_uid" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="get_balanceResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="balance" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>
    
    <!-- Authentication Messages -->
    <message name="register_userRequest">
        <part name="parameters" element="tns:register_user"/>
    </message>
    <message name="register_userResponse">
        <part name="parameters" element="tns:register_userResponse"/>
    </message>
    
    <message name="login_userRequest">
        <part name="parameters" element="tns:login_user"/>
    </message>
    <message name="login_userResponse">
        <part name="parameters" element="tns:login_userResponse"/>
    </message>
    
    <message name="logout_userRequest">
        <part name="parameters" element="tns:logout_user"/>
    </message>
    <message name="logout_userResponse">
        <part name="parameters" element="tns:logout_userResponse"/>
    </message>
    
    <!-- Wallet Messages -->
    <message name="register_walletRequest">
        <part name="parameters" element="tns:register_wallet"/>
    </message>
    <message name="register_walletResponse">
        <part name="parameters" element="tns:register_walletResponse"/>
    </message>
    
    <message name="top_upRequest">
        <part name="parameters" element="tns:top_up"/>
    </message>
    <message name="top_upResponse">
        <part name="parameters" element="tns:top_upResponse"/>
    </message>
    
    <message name="paymentRequest">
        <part name="parameters" element="tns:payment"/>
    </message>
    <message name="paymentResponse">
        <part name="parameters" element="tns:paymentResponse"/>
    </message>
    
    <message name="get_balanceRequest">
        <part name="parameters" element="tns:get_balance"/>
    </message>
    <message name="get_balanceResponse">
        <part name="parameters" element="tns:get_balanceResponse"/>
    </message>
    
    <portType name="WalletPortType">
        <!-- Authentication Operations -->
        <operation name="register_user">
            <input message="tns:register_userRequest"/>
            <output message="tns:register_userResponse"/>
        </operation>
        <operation name="login_user">
            <input message="tns:login_userRequest"/>
            <output message="tns:login_userResponse"/>
        </operation>
        <operation name="logout_user">
            <input message="tns:logout_userRequest"/>
            <output message="tns:logout_userResponse"/>
        </operation>
        
        <!-- Wallet Operations -->
        <operation name="register_wallet">
            <input message="tns:register_walletRequest"/>
            <output message="tns:register_walletResponse"/>
        </operation>
        <operation name="top_up">
            <input message="tns:top_upRequest"/>
            <output message="tns:top_upResponse"/>
        </operation>
        <operation name="payment">
            <input message="tns:paymentRequest"/>
            <output message="tns:paymentResponse"/>
        </operation>
        <operation name="get_balance">
            <input message="tns:get_balanceRequest"/>
            <output message="tns:get_balanceResponse"/>
        </operation>
    </portType>
    
    <binding name="WalletBinding" type="tns:WalletPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        
        <!-- Authentication Operations -->
        <operation name="register_user">
            <soap:operation soapAction="register_user"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="login_user">
            <soap:operation soapAction="login_user"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="logout_user">
            <soap:operation soapAction="logout_user"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        
        <!-- Wallet Operations -->
        <operation name="register_wallet">
            <soap:operation soapAction="register_wallet"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="top_up">
            <soap:operation soapAction="top_up"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="payment">
            <soap:operation soapAction="payment"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
        <operation name="get_balance">
            <soap:operation soapAction="get_balance"/>
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
    </binding>
    
    <service name="WalletService">
        <port name="WalletPort" binding="tns:WalletBinding">
            <soap:address location="http://localhost:8000/"/>
        </port>
    </service>
</definitions>'''
    return Response(wsdl, mimetype='text/xml')

if __name__ == '__main__':
    # Get configuration
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', '8000'))
    
    logger.info(f"Starting SOAP Wallet Service on {host}:{port}")
    logger.info(f"Database connected: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # Start Flask application
    app.run(host=host, port=port, debug=False)
