"""
SOAP API implementation for the Enhanced User Management System
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import XMLResponse
from spyne import Application, rpc, ServiceBase, Unicode, Integer, Boolean, DateTime
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.primitive import String
from spyne.model.complex import Iterable
from datetime import datetime
import structlog
from typing import Dict, Any

from src.config.settings import settings
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.role_service import RoleService
from src.services.audit_service import AuditService
from src.database.connection import get_database_session

logger = structlog.get_logger()


class UserManagementService(ServiceBase):
    """Main SOAP service for user management operations"""
    
    @rpc(String, String, String, String, String, _returns=String)
    async def RegisterUser(ctx, email, password, firstName, lastName, phoneNumber):
        """Register a new user"""
        try:
            user_service = UserService()
            audit_service = AuditService()
            
            # Register user
            result = user_service.register_user(
                email=email,
                password=password,
                first_name=firstName,
                last_name=lastName,
                phone_number=phoneNumber
            )
            
            # Log audit event
            audit_service.log_event(
                user_id=result.get('user_id'),
                action='USER_REGISTERED',
                resource_type='USER',
                resource_id=result.get('user_id'),
                new_values=str(result)
            )
            
            # Return SOAP response
            return self._format_success_response(result, "User registered successfully")
            
        except Exception as e:
            logger.error("User registration failed", error=str(e))
            return self._format_error_response("USER_001", str(e))
    
    @rpc(String, String, _returns=String)
    async def AuthenticateUser(ctx, email, password):
        """Authenticate user and return token"""
        try:
            auth_service = AuthService()
            audit_service = AuditService()
            
            # Authenticate user
            result = auth_service.authenticate_user(email, password)
            
            if result.get('success'):
                # Log successful login
                audit_service.log_event(
                    user_id=result.get('user_id'),
                    action='USER_LOGIN_SUCCESS',
                    resource_type='USER',
                    resource_id=result.get('user_id')
                )
                
                return self._format_success_response(result, "Authentication successful")
            else:
                # Log failed login
                audit_service.log_event(
                    user_id=None,
                    action='USER_LOGIN_FAILED',
                    resource_type='USER',
                    new_values={'email': email, 'reason': result.get('message', 'Invalid credentials')}
                )
                
                return self._format_error_response("AUTH_001", "Invalid credentials")
                
        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            return self._format_error_response("AUTH_001", str(e))
    
    @rpc(String, _returns=String)
    async def LogoutUser(ctx, token):
        """Logout user and invalidate token"""
        try:
            auth_service = AuthService()
            audit_service = AuditService()
            
            # Validate token and get user info
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Logout user
            result = auth_service.logout_user(token)
            
            # Log logout event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='USER_LOGOUT',
                resource_type='USER',
                resource_id=user_info.get('user_id')
            )
            
            return self._format_success_response(result, "Logout successful")
            
        except Exception as e:
            logger.error("Logout failed", error=str(e))
            return self._format_error_response("AUTH_002", str(e))
    
    @rpc(String, Integer, _returns=String)
    async def GetUserProfile(ctx, token, userId=None):
        """Get user profile information"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Get user profile
            target_user_id = userId or user_info.get('user_id')
            result = user_service.get_user_profile(
                requesting_user_id=user_info.get('user_id'),
                target_user_id=target_user_id
            )
            
            return self._format_success_response(result, "Profile retrieved successfully")
            
        except Exception as e:
            logger.error("Get user profile failed", error=str(e))
            return self._format_error_response("USER_001", str(e))
    
    @rpc(String, Integer, String, String, String, String, _returns=String)
    async def UpdateUserProfile(ctx, token, userId=None, firstName=None, lastName=None, phoneNumber=None, profilePictureUrl=None):
        """Update user profile information"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Update user profile
            target_user_id = userId or user_info.get('user_id')
            update_data = {}
            if firstName:
                update_data['first_name'] = firstName
            if lastName:
                update_data['last_name'] = lastName
            if phoneNumber:
                update_data['phone_number'] = phoneNumber
            if profilePictureUrl:
                update_data['profile_picture_url'] = profilePictureUrl
            
            result = user_service.update_user_profile(
                requesting_user_id=user_info.get('user_id'),
                target_user_id=target_user_id,
                update_data=update_data
            )
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='USER_PROFILE_UPDATED',
                resource_type='USER',
                resource_id=target_user_id,
                new_values=str(update_data)
            )
            
            return self._format_success_response(result, "Profile updated successfully")
            
        except Exception as e:
            logger.error("Update user profile failed", error=str(e))
            return self._format_error_response("USER_001", str(e))
    
    @rpc(String, Integer, Integer, String, _returns=String)
    async def GetAllUsers(ctx, token, page=1, pageSize=20, status=None):
        """Get all users with pagination"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Get all users
            result = user_service.get_all_users(
                requesting_user_id=user_info.get('user_id'),
                page=page,
                page_size=pageSize,
                status=status
            )
            
            return self._format_success_response(result, "Users retrieved successfully")
            
        except Exception as e:
            logger.error("Get all users failed", error=str(e))
            return self._format_error_response("USER_001", str(e))
    
    @rpc(String, Integer, _returns=String)
    async def DeactivateUser(ctx, token, userId):
        """Deactivate a user"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Deactivate user
            result = user_service.deactivate_user(
                requesting_user_id=user_info.get('user_id'),
                target_user_id=userId
            )
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='USER_DEACTIVATED',
                resource_type='USER',
                resource_id=userId
            )
            
            return self._format_success_response(result, "User deactivated successfully")
            
        except Exception as e:
            logger.error("Deactivate user failed", error=str(e))
            return self._format_error_response("USER_003", str(e))
    
    @rpc(String, String, String, _returns=String)
    async def CreateRole(ctx, token, name, description=None):
        """Create a new role"""
        try:
            auth_service = AuthService()
            role_service = RoleService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Check authorization
            async with get_database_session() as session:
                from src.models.user import User
                requesting_user = await User.find_by_id(session, user_info.get('user_id'))
                if not requesting_user or not await requesting_user.has_permission(session, "ROLE_CREATE"):
                    return self._format_error_response("AUTH_003", "Insufficient permissions")
            
            # Create role
            result = role_service.create_role(name, description)
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='ROLE_CREATED',
                resource_type='ROLE',
                resource_id=result.get('role_id'),
                new_values=str(result)
            )
            
            return self._format_success_response(result, "Role created successfully")
            
        except Exception as e:
            logger.error("Create role failed", error=str(e))
            return self._format_error_response("ROLE_001", str(e))
    
    @rpc(String, Integer, Integer, _returns=String)
    async def AssignRole(ctx, token, userId, roleId):
        """Assign a role to a user"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Assign role
            result = user_service.assign_role(
                requesting_user_id=user_info.get('user_id'),
                target_user_id=userId,
                role_id=roleId
            )
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='ROLE_ASSIGNED',
                resource_type='USER_ROLE',
                resource_id=userId,
                new_values=f"role_id={roleId}"
            )
            
            return self._format_success_response(result, "Role assigned successfully")
            
        except Exception as e:
            logger.error("Assign role failed", error=str(e))
            return self._format_error_response("ROLE_002", str(e))
    
    @rpc(String, Integer, _returns=String)
    async def GetUserRoles(ctx, token, userId=None):
        """Get user's roles"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Get user roles
            result = user_service.get_user_roles(
                requesting_user_id=user_info.get('user_id'),
                target_user_id=userId
            )
            
            return self._format_success_response(result, "User roles retrieved successfully")
            
        except Exception as e:
            logger.error("Get user roles failed", error=str(e))
            return self._format_error_response("ROLE_001", str(e))
    
    @rpc(String, String, String, String, String, _returns=String)
    async def CreatePermission(ctx, token, name, description=None, module=None, action=None):
        """Create a new permission"""
        try:
            auth_service = AuthService()
            role_service = RoleService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Check authorization
            async with get_database_session() as session:
                from src.models.user import User
                requesting_user = await User.find_by_id(session, user_info.get('user_id'))
                if not requesting_user or not await requesting_user.has_permission(session, "PERMISSION_CREATE"):
                    return self._format_error_response("AUTH_003", "Insufficient permissions")
            
            # Create permission
            result = role_service.create_permission(name, description, module, action)
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='PERMISSION_CREATED',
                resource_type='PERMISSION',
                resource_id=result.get('permission_id'),
                new_values=str(result)
            )
            
            return self._format_success_response(result, "Permission created successfully")
            
        except Exception as e:
            logger.error("Create permission failed", error=str(e))
            return self._format_error_response("PERM_001", str(e))
    
    @rpc(String, Integer, Integer, _returns=String)
    async def AssignPermissionToRole(ctx, token, roleId, permissionId):
        """Assign a permission to a role"""
        try:
            auth_service = AuthService()
            role_service = RoleService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Check authorization
            async with get_database_session() as session:
                from src.models.user import User
                requesting_user = await User.find_by_id(session, user_info.get('user_id'))
                if not requesting_user or not await requesting_user.has_permission(session, "PERMISSION_ASSIGN"):
                    return self._format_error_response("AUTH_003", "Insufficient permissions")
            
            # Assign permission to role
            result = role_service.assign_permission_to_role(
                role_id=roleId,
                permission_id=permissionId,
                assigned_by=user_info.get('user_id')
            )
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='PERMISSION_ASSIGNED',
                resource_type='ROLE_PERMISSION',
                resource_id=roleId,
                new_values=f"permission_id={permissionId}"
            )
            
            return self._format_success_response(result, "Permission assigned to role successfully")
            
        except Exception as e:
            logger.error("Assign permission to role failed", error=str(e))
            return self._format_error_response("PERM_002", str(e))
    
    @rpc(String, _returns=String)
    async def RequestPasswordReset(ctx, email):
        """Request password reset"""
        try:
            user_service = UserService()
            audit_service = AuditService()
            
            # Request password reset
            result = user_service.request_password_reset(email)
            
            # Log audit event
            audit_service.log_event(
                user_id=None,
                action='PASSWORD_RESET_REQUESTED',
                resource_type='USER',
                new_values={'email': email}
            )
            
            return self._format_success_response(result, "Password reset email sent")
            
        except Exception as e:
            logger.error("Request password reset failed", error=str(e))
            return self._format_error_response("AUTH_001", str(e))
    
    @rpc(String, String, _returns=String)
    async def ResetPassword(ctx, resetToken, newPassword):
        """Reset password using reset token"""
        try:
            user_service = UserService()
            audit_service = AuditService()
            
            # Reset password
            result = user_service.reset_password(resetToken, newPassword)
            
            # Log audit event
            audit_service.log_event(
                user_id=None,
                action='PASSWORD_RESET_COMPLETED',
                resource_type='USER',
                new_values={'token_used': resetToken}
            )
            
            return self._format_success_response(result, "Password reset successfully")
            
        except Exception as e:
            logger.error("Reset password failed", error=str(e))
            return self._format_error_response("AUTH_001", str(e))
    
    @rpc(String, String, String, _returns=String)
    async def ChangePassword(ctx, token, currentPassword, newPassword):
        """Change user password"""
        try:
            auth_service = AuthService()
            user_service = UserService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Change password
            result = user_service.change_password(
                user_id=user_info.get('user_id'),
                current_password=currentPassword,
                new_password=newPassword
            )
            
            # Log audit event
            audit_service.log_event(
                user_id=user_info.get('user_id'),
                action='PASSWORD_CHANGED',
                resource_type='USER',
                resource_id=user_info.get('user_id')
            )
            
            return self._format_success_response(result, "Password changed successfully")
            
        except Exception as e:
            logger.error("Change password failed", error=str(e))
            return self._format_error_response("AUTH_001", str(e))
    
    @rpc(String, String, String, String, String, Integer, Integer, Integer, Integer, _returns=String)
    def GetAuditLogs(ctx, token, startDate=None, endDate=None, userId=None,
                    action=None, resourceType=None, page=1, pageSize=20):
        """Get audit logs with filtering"""
        try:
            auth_service = AuthService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Check authorization
            async with get_database_session() as session:
                from src.models.user import User
                requesting_user = await User.find_by_id(session, user_info.get('user_id'))
                if not requesting_user or not await requesting_user.has_permission(session, "AUDIT_READ"):
                    return self._format_error_response("AUTH_003", "Insufficient permissions")
            
            # Parse dates
            from datetime import datetime
            start_date = None
            end_date = None
            if startDate:
                try:
                    start_date = datetime.fromisoformat(startDate.replace('Z', '+00:00'))
                except:
                    pass
            if endDate:
                try:
                    end_date = datetime.fromisoformat(endDate.replace('Z', '+00:00'))
                except:
                    pass
            
            # Get audit logs
            result = audit_service.get_audit_logs(
                user_id=userId,
                action=action,
                resource_type=resourceType,
                start_date=start_date,
                end_date=end_date,
                page=page,
                page_size=pageSize
            )
            
            return self._format_success_response(result, "Audit logs retrieved successfully")
            
        except Exception as e:
            logger.error("Get audit logs failed", error=str(e))
            return self._format_error_response("AUDIT_001", str(e))
    
    @rpc(String, Integer, String, String, Integer, Integer, _returns=String)
    async def GetUserAuditLogs(ctx, token, userId=None, startDate=None,
                        endDate=None, page=1, pageSize=20):
        """Get audit logs for a specific user"""
        try:
            auth_service = AuthService()
            audit_service = AuditService()
            
            # Validate token
            user_info = auth_service.validate_token(token)
            if not user_info:
                return self._format_error_response("AUTH_002", "Invalid token")
            
            # Check authorization (users can view their own logs, others need AUDIT_READ)
            target_user_id = userId or user_info.get('user_id')
            if target_user_id != user_info.get('user_id'):
                async with get_database_session() as session:
                    from src.models.user import User
                    requesting_user = await User.find_by_id(session, user_info.get('user_id'))
                    if not requesting_user or not await requesting_user.has_permission(session, "AUDIT_READ"):
                        return self._format_error_response("AUTH_003", "Insufficient permissions")
            
            # Parse dates
            from datetime import datetime
            start_date = None
            end_date = None
            if startDate:
                try:
                    start_date = datetime.fromisoformat(startDate.replace('Z', '+00:00'))
                except:
                    pass
            if endDate:
                try:
                    end_date = datetime.fromisoformat(endDate.replace('Z', '+00:00'))
                except:
                    pass
            
            # Get user audit logs
            result = audit_service.get_user_audit_logs(
                target_user_id=target_user_id,
                start_date=start_date,
                end_date=end_date,
                page=page,
                page_size=pageSize
            )
            
            return self._format_success_response(result, "User audit logs retrieved successfully")
            
        except Exception as e:
            logger.error("Get user audit logs failed", error=str(e))
            return self._format_error_response("AUDIT_001", str(e))
    
    def _format_success_response(self, data: Dict[str, Any], message: str) -> str:
        """Format successful SOAP response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        return self._dict_to_xml(response)
    
    def _format_error_response(self, code: str, message: str) -> str:
        """Format error SOAP response"""
        response = {
            "success": False,
            "error": {
                "code": code,
                "message": message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        return self._dict_to_xml(response)
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to XML string (simplified implementation)"""
        # This is a simplified XML conversion
        # In production, use proper XML serialization
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">')
        xml_parts.append('<soap:Body>')
        
        def dict_to_xml_recursive(d, parent_key=""):
            for key, value in d.items():
                if isinstance(value, dict):
                    xml_parts.append(f'<{key}>')
                    dict_to_xml_recursive(value, key)
                    xml_parts.append(f'</{key}>')
                elif isinstance(value, list):
                    for item in value:
                        xml_parts.append(f'<{key}>')
                        if isinstance(item, dict):
                            dict_to_xml_recursive(item, key)
                        else:
                            xml_parts.append(str(item))
                        xml_parts.append(f'</{key}>')
                else:
                    xml_parts.append(f'<{key}>{value}</{key}>')
        
        dict_to_xml_recursive(data)
        xml_parts.append('</soap:Body>')
        xml_parts.append('</soap:Envelope>')
        
        return '\n'.join(xml_parts)


def create_soap_app() -> FastAPI:
    """Create FastAPI application with SOAP support"""
    
    # Create Spyne SOAP application
    soap_app = Application(
        [UserManagementService],
        'user.management.soap',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    
    # Create WSGI application
    wsgi_app = WsgiApplication(soap_app)
    
    # Create FastAPI wrapper
    app = FastAPI()
    
    @app.post("/")
    async def soap_endpoint(request: Request):
        """Handle SOAP requests"""
        try:
            # Get request body
            body = await request.body()
            
            # Create WSGI environment
            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': request.headers.get('content-type', 'text/xml'),
                'CONTENT_LENGTH': str(len(body)),
                'wsgi.input': type('MockInput', (), {'read': lambda: body})(),
                'wsgi.version': (1, 0),
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,
                'wsgi.errors': None,
                'wsgi.url_scheme': 'http',
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': str(settings.APP_PORT),
                'PATH_INFO': '/',
                'SCRIPT_NAME': '',
                'QUERY_STRING': '',
                'HTTP_SOAPACTION': request.headers.get('soapaction', ''),
            }
            
            # Add headers to environ
            for key, value in request.headers.items():
                environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
            
            # Call WSGI application
            def start_response(status, response_headers):
                pass
            
            response = wsgi_app(environ, start_response)
            
            # Return response
            return XMLResponse(content=b''.join(response))
            
        except Exception as e:
            logger.error("SOAP request processing failed", error=str(e))
            return XMLResponse(
                content=f'<?xml version="1.0" encoding="UTF-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><soap:Fault><faultcode>soap:Server</faultcode><faultstring>Internal server error: {str(e)}</faultstring></soap:Fault></soap:Body></soap:Envelope>',
                status_code=500
            )
    
    @app.get("/wsdl")
    async def wsdl_endpoint():
        """Serve WSDL file"""
        # This should return the actual WSDL content
        # For now, return a placeholder
        wsdl_content = """<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:tns="http://example.com/usermanagement"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  targetNamespace="http://example.com/usermanagement">
    <!-- WSDL content would go here -->
    <wsdl:service name="UserManagementService">
        <wsdl:port name="UserManagementPort" binding="tns:UserManagementSoapBinding">
            <soap:address location="http://localhost:8000/soap"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""
        
        return XMLResponse(content=wsdl_content)
    
    return app