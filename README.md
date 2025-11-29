# Customer Management SOAP Service

This is a simple SOAP API backend designed for practicing Robot Framework testing.

## Tech Stack
- **Backend**: Python 3.9 (Flask + Spyne)
- **Database**: PostgreSQL 16
- **Infrastructure**: Docker Compose

## Getting Started

### Prerequisites
- Docker and Docker Compose installed.

### Run the Service
1. Open a terminal in this directory.
2. Run the following command:
   ```bash
   docker-compose up --build
   ```
3. Wait for the service to start. You should see logs indicating the database is initialized and the server is running.

### Access the Service
- **WSDL URL**: `http://localhost:8000/soap?wsdl`
- **Home Page**: `http://localhost:8000/`

## Service Documentation

### Data Model: Customer
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique ID (Auto-generated) |
| `full_name` | String | Customer's full name |
| `email` | String | Email address (Unique) |
| `phone_number` | String | Phone number |
| `status` | String | 'ACTIVE' or 'INACTIVE' |

### Operations

#### 1. `create_customer`
- **Input**: `full_name`, `email`, `phone_number`
- **Output**: String (Success message with ID or Error message)

#### 2. `get_customer`
- **Input**: `customer_id`
- **Output**: `CustomerModel` object (or null if not found)

#### 3. `update_customer`
- **Input**: `customer_id`, `full_name`, `email`, `phone_number`, `status`
- **Output**: Boolean (`true` if success, `false` otherwise)

#### 4. `delete_customer`
- **Input**: `customer_id`
- **Output**: Boolean (`true` if success, `false` otherwise)

#### 5. `get_all_customers`
- **Input**: None
- **Output**: Array of `CustomerModel`

## Testing with curl

You can test the API using `curl`. Here is an example to create a customer:

```bash
curl -X POST -H "Content-Type: text/xml" -d '
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:spy="spyne.examples.hello.soap">
   <soapenv:Header/>
   <soapenv:Body>
      <spy:create_customer>
         <spy:full_name>John Doe</spy:full_name>
         <spy:email>john@example.com</spy:email>
         <spy:phone_number>1234567890</spy:phone_number>
      </spy:create_customer>
   </soapenv:Body>
</soapenv:Envelope>' http://localhost:8000/soap
```
