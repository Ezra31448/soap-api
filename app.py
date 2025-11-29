from flask import Flask
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Iterable, Boolean, Array
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from models import init_db, Session, Customer
from auth_service import AuthService
from auth_middleware import check_authentication
import logging

# Define a Complex Model for Customer Return
from spyne.model.complex import ComplexModel

class CustomerModel(ComplexModel):
    id = Integer
    full_name = Unicode
    email = Unicode
    phone_number = Unicode
    status = Unicode

class CustomerService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def create_customer(ctx, full_name, email, phone_number):
        # Check authentication
        user_id, username = check_authentication(ctx)
        
        session = Session()
        try:
            new_customer = Customer(full_name=full_name, email=email, phone_number=phone_number, status='ACTIVE')
            session.add(new_customer)
            session.commit()
            return f"SUCCESS: Created customer with ID {new_customer.id}"
        except Exception as e:
            session.rollback()
            return f"ERROR: {str(e)}"
        finally:
            session.close()

    @rpc(Integer, _returns=CustomerModel)
    def get_customer(ctx, customer_id):
        # Check authentication
        user_id, username = check_authentication(ctx)
        
        session = Session()
        try:
            c = session.query(Customer).filter_by(id=customer_id).first()
            if c:
                return CustomerModel(
                    id=c.id,
                    full_name=c.full_name,
                    email=c.email,
                    phone_number=c.phone_number,
                    status=c.status
                )
            return None
        finally:
            session.close()

    @rpc(Integer, Unicode, Unicode, Unicode, Unicode, _returns=Boolean)
    def update_customer(ctx, customer_id, full_name, email, phone_number, status):
        # Check authentication
        user_id, username = check_authentication(ctx)
        
        session = Session()
        try:
            c = session.query(Customer).filter_by(id=customer_id).first()
            if c:
                c.full_name = full_name
                c.email = email
                c.phone_number = phone_number
                c.status = status
                session.commit()
                return True
            return False
        except:
            session.rollback()
            return False
        finally:
            session.close()

    @rpc(Integer, _returns=Boolean)
    def delete_customer(ctx, customer_id):
        # Check authentication
        user_id, username = check_authentication(ctx)
        
        session = Session()
        try:
            c = session.query(Customer).filter_by(id=customer_id).first()
            if c:
                session.delete(c)
                session.commit()
                return True
            return False
        except:
            session.rollback()
            return False
        finally:
            session.close()

    @rpc(_returns=Iterable(CustomerModel))
    def get_all_customers(ctx):
        # Check authentication
        user_id, username = check_authentication(ctx)
        
        session = Session()
        try:
            customers = session.query(Customer).all()
            for c in customers:
                yield CustomerModel(
                    id=c.id,
                    full_name=c.full_name,
                    email=c.email,
                    phone_number=c.phone_number,
                    status=c.status
                )
        finally:
            session.close()

app = Flask(__name__)

# Create Spyne Application with both services
soap_app = Application([CustomerService, AuthService], 'spyne.examples.hello.soap',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())

# Wrap with WSGI
wsgi_app = WsgiApplication(soap_app)

# Mount Spyne app at /soap
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/soap': wsgi_app
})

@app.route('/')
def index():
    return "SOAP API is running. WSDL available at <a href='/soap?wsdl'>/soap?wsdl</a>"

if __name__ == '__main__':
    print("Initializing Database...")
    init_db()
    print("Starting Flask Server...")
    app.run(host='0.0.0.0', port=8000)
