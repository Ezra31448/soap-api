# Postman Collection Instructions for SOAP Wallet API with Authentication

## Overview
This Postman collection provides a complete set of requests to test the SOAP Wallet API service with JWT authentication. The API runs on `http://localhost:8001` and provides wallet management operations with secure authentication.

## Prerequisites
1. **Start the SOAP API service**:
   ```bash
   docker-compose up --build
   ```
2. **Install Postman** (if not already installed)
3. **Import the collection** into Postman

## Importing the Collection

### Method 1: Import from File
1. Open Postman
2. Click **Import** button
3. Select the `soap-wallet-api-postman-collection.json` file
4. Click **Import**

### Method 2: Import from Raw Text
1. Open Postman
2. Click **Import** button
3. Select **Raw Text** tab
4. Copy and paste the JSON content from `soap-wallet-api-postman-collection.json`
5. Click **Import**

## Collection Structure

The collection contains 5 requests:

### 1. Get WSDL
- **Method**: GET
- **URL**: `http://localhost:8001/?wsdl`
- **Purpose**: Retrieve the WSDL definition for the SOAP service
- **Expected Response**: XML WSDL document

### 2. Register Wallet
- **Method**: POST
- **URL**: `http://localhost:8001/`
- **Headers**: 
  - `Content-Type: text/xml; charset=utf-8`
  - `SOAPAction: register_wallet`
- **Body**: SOAP envelope with username and email
- **Purpose**: Create a new wallet for a user
- **Expected Response**: XML with wallet_uid

### 3. Top Up Wallet
- **Method**: POST
- **URL**: `http://localhost:8001/`
- **Headers**: 
  - `Content-Type: text/xml; charset=utf-8`
  - `SOAPAction: top_up`
- **Body**: SOAP envelope with wallet_uid and amount
- **Purpose**: Add funds to an existing wallet
- **Expected Response**: XML with success message and new balance

### 4. Make Payment
- **Method**: POST
- **URL**: `http://localhost:8001/`
- **Headers**: 
  - `Content-Type: text/xml; charset=utf-8`
  - `SOAPAction: payment`
- **Body**: SOAP envelope with wallet_uid and amount
- **Purpose**: Deduct funds from wallet (payment)
- **Expected Response**: XML with success message and remaining balance

### 5. Get Balance
- **Method**: POST
- **URL**: `http://localhost:8001/`
- **Headers**: 
  - `Content-Type: text/xml; charset=utf-8`
  - `SOAPAction: get_balance`
- **Body**: SOAP envelope with wallet_uid
- **Purpose**: Get current wallet balance
- **Expected Response**: XML with current balance

## Environment Variables

The collection uses the following variables:
- `{{username}}` - Default: "testuser"
- `{{email}}` - Default: "test@example.com"
- `{{wallet_uid}}` - Default: "your_wallet_uid_here"
- `{{amount}}` - Default: "100.00"

### How to Update Variables

1. **Collection Variables**:
   - Click on the collection name
   - Go to **Variables** tab
   - Update the values as needed

2. **Environment Variables** (Recommended):
   - Create a new environment in Postman
   - Add the variables with your desired values
   - Select the environment from the dropdown

## Testing Workflow

### Step 1: Get WSDL
- Run the "Get WSDL" request to verify the service is running
- You should receive an XML WSDL document

### Step 2: Register a Wallet
- Update the `username` and `email` variables
- Run the "Register Wallet" request
- **Save the returned `wallet_uid`** for subsequent requests
- Update the `wallet_uid` variable with the returned value

### Step 3: Test Wallet Operations
1. **Top Up**: Add funds to the wallet
2. **Get Balance**: Check the current balance
3. **Make Payment**: Deduct funds from the wallet
4. **Get Balance**: Verify the remaining balance

### Example Workflow:
```
Register Wallet → Top Up (100.00) → Get Balance (should be 100.00) → 
Payment (50.00) → Get Balance (should be 50.00)
```

## Error Handling

The collection includes test scripts that:
- Verify HTTP status code is 200
- Check response content type is XML
- Detect SOAP faults in responses

### Common SOAP Faults:
- **WALLET_NOT_FOUND**: Invalid wallet_uid
- **INSUFFICIENT_BALANCE**: Not enough funds for payment
- **DUPLICATE_USER**: Username or email already exists
- **INVALID_AMOUNT**: Amount is not positive

## Tips for Testing

1. **Start Fresh**: If you encounter errors, restart the Docker containers
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Use Unique Values**: For testing multiple users, use unique usernames and emails

3. **Check Logs**: If requests fail, check the Docker logs
   ```bash
   docker-compose logs -f wallet-api
   ```

4. **Database Reset**: To reset the database, stop containers and remove volumes
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

## Troubleshooting

### Service Not Running
- Ensure Docker is running
- Check if containers are started: `docker ps`
- Verify port 8001 is available

### Connection Refused
- Check if the API service is running: `docker-compose logs wallet-api`
- Verify the URL is correct: `http://localhost:8001/`

### SOAP Faults
- Check the request body format
- Verify all required parameters are provided
- Ensure wallet_uid is valid (from register_wallet response)

### XML Parsing Errors
- Verify the SOAP envelope format
- Check for proper namespace declarations
- Ensure proper XML encoding

## Sample Request/Response

### Register Wallet Request:
```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wallet="wallet.soap">
  <soap:Body>
    <wallet:register_wallet>
      <wallet:username>john_doe</wallet:username>
      <wallet:email>john@example.com</wallet:email>
    </wallet:register_wallet>
  </soap:Body>
</soap:Envelope>
```

### Register Wallet Response:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wallet="wallet.soap">
  <soap:Body>
    <wallet:register_walletResponse>
      <wallet:wallet_uid>123e4567-e89b-12d3-a456-426614174000</wallet:wallet_uid>
    </wallet:register_walletResponse>
  </soap:Body>
</soap:Envelope>
```

This collection provides a complete testing environment for the SOAP Wallet API. Use the workflow described above to test all functionality.
