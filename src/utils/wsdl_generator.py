"""
WSDL document generator for Enhanced User Management System
"""
from datetime import datetime


def generate_wsdl() -> str:
    """Generate complete WSDL document"""
    
    wsdl_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:tns="http://example.com/usermanagement"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"
                  targetNamespace="http://example.com/usermanagement">

    <!-- Types Section -->
    <wsdl:types>
        <xsd:schema targetNamespace="http://example.com/usermanagement"
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                   elementFormDefault="qualified">

            <!-- Common Types -->
            <xsd:complexType name="AuthHeader">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ErrorResponse">
                <xsd:sequence>
                    <xsd:element name="code" type="xsd:string"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="details" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="SuccessResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- User Types -->
            <xsd:complexType name="User">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:int"/>
                    <xsd:element name="email" type="xsd:string"/>
                    <xsd:element name="firstName" type="xsd:string"/>
                    <xsd:element name="lastName" type="xsd:string"/>
                    <xsd:element name="phoneNumber" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="profilePictureUrl" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="status" type="xsd:string"/>
                    <xsd:element name="createdAt" type="xsd:dateTime"/>
                    <xsd:element name="updatedAt" type="xsd:dateTime"/>
                    <xsd:element name="lastLogin" type="xsd:dateTime" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ArrayOfUser">
                <xsd:sequence>
                    <xsd:element name="user" type="tns:User" maxOccurs="unbounded" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Role Types -->
            <xsd:complexType name="Role">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:int"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="createdAt" type="xsd:dateTime"/>
                    <xsd:element name="updatedAt" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ArrayOfRole">
                <xsd:sequence>
                    <xsd:element name="role" type="tns:Role" maxOccurs="unbounded" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Permission Types -->
            <xsd:complexType name="Permission">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:int"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="module" type="xsd:string"/>
                    <xsd:element name="action" type="xsd:string"/>
                    <xsd:element name="createdAt" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ArrayOfPermission">
                <xsd:sequence>
                    <xsd:element name="permission" type="tns:Permission" maxOccurs="unbounded" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Audit Types -->
            <xsd:complexType name="AuditLog">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:int"/>
                    <xsd:element name="userId" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="action" type="xsd:string"/>
                    <xsd:element name="resourceType" type="xsd:string"/>
                    <xsd:element name="resourceId" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="oldValues" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="newValues" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="ipAddress" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="userAgent" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="createdAt" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ArrayOfAuditLog">
                <xsd:sequence>
                    <xsd:element name="auditLog" type="tns:AuditLog" maxOccurs="unbounded" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Authentication Request/Response Types -->
            <xsd:complexType name="RegisterUserRequest">
                <xsd:sequence>
                    <xsd:element name="email" type="xsd:string"/>
                    <xsd:element name="password" type="xsd:string"/>
                    <xsd:element name="firstName" type="xsd:string"/>
                    <xsd:element name="lastName" type="xsd:string"/>
                    <xsd:element name="phoneNumber" type="xsd:string" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="RegisterUserResponse">
                <xsd:sequence>
                    <xsd:element name="userId" type="xsd:int"/>
                    <xsd:element name="email" type="xsd:string"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="AuthenticateUserRequest">
                <xsd:sequence>
                    <xsd:element name="email" type="xsd:string"/>
                    <xsd:element name="password" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="AuthenticateUserResponse">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int"/>
                    <xsd:element name="roles" type="tns:ArrayOfString"/>
                    <xsd:element name="expiresIn" type="xsd:int"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="LogoutUserRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="LogoutUserResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- User Management Request/Response Types -->
            <xsd:complexType name="GetUserProfileRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetUserProfileResponse">
                <xsd:sequence>
                    <xsd:element name="user" type="tns:User"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="UpdateUserProfileRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="firstName" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="lastName" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="phoneNumber" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="profilePictureUrl" type="xsd:string" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="UpdateUserProfileResponse">
                <xsd:sequence>
                    <xsd:element name="user" type="tns:User"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetAllUsersRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="page" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="pageSize" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="status" type="xsd:string" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetAllUsersResponse">
                <xsd:sequence>
                    <xsd:element name="users" type="tns:ArrayOfUser"/>
                    <xsd:element name="totalCount" type="xsd:int"/>
                    <xsd:element name="page" type="xsd:int"/>
                    <xsd:element name="pageSize" type="xsd:int"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="DeactivateUserRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="DeactivateUserResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Role Management Request/Response Types -->
            <xsd:complexType name="CreateRoleRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="CreateRoleResponse">
                <xsd:sequence>
                    <xsd:element name="role" type="tns:Role"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="AssignRoleRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int"/>
                    <xsd:element name="roleId" type="xsd:int"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="AssignRoleResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetUserRolesRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetUserRolesResponse">
                <xsd:sequence>
                    <xsd:element name="roles" type="tns:ArrayOfRole"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Permission Management Request/Response Types -->
            <xsd:complexType name="CreatePermissionRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="module" type="xsd:string"/>
                    <xsd:element name="action" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="CreatePermissionResponse">
                <xsd:sequence>
                    <xsd:element name="permission" type="tns:Permission"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="AssignPermissionToRoleRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="roleId" type="xsd:int"/>
                    <xsd:element name="permissionId" type="xsd:int"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="AssignPermissionToRoleResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Password Management Request/Response Types -->
            <xsd:complexType name="RequestPasswordResetRequest">
                <xsd:sequence>
                    <xsd:element name="email" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="RequestPasswordResetResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ResetPasswordRequest">
                <xsd:sequence>
                    <xsd:element name="resetToken" type="xsd:string"/>
                    <xsd:element name="newPassword" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ResetPasswordResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ChangePasswordRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="currentPassword" type="xsd:string"/>
                    <xsd:element name="newPassword" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="ChangePasswordResponse">
                <xsd:sequence>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Audit Request/Response Types -->
            <xsd:complexType name="GetAuditLogsRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="startDate" type="xsd:dateTime" minOccurs="0"/>
                    <xsd:element name="endDate" type="xsd:dateTime" minOccurs="0"/>
                    <xsd:element name="userId" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="action" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="resourceType" type="xsd:string" minOccurs="0"/>
                    <xsd:element name="page" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="pageSize" type="xsd:int" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetAuditLogsResponse">
                <xsd:sequence>
                    <xsd:element name="auditLogs" type="tns:ArrayOfAuditLog"/>
                    <xsd:element name="totalCount" type="xsd:int"/>
                    <xsd:element name="page" type="xsd:int"/>
                    <xsd:element name="pageSize" type="xsd:int"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetUserAuditLogsRequest">
                <xsd:sequence>
                    <xsd:element name="token" type="xsd:string"/>
                    <xsd:element name="userId" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="startDate" type="xsd:dateTime" minOccurs="0"/>
                    <xsd:element name="endDate" type="xsd:dateTime" minOccurs="0"/>
                    <xsd:element name="page" type="xsd:int" minOccurs="0"/>
                    <xsd:element name="pageSize" type="xsd:int" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

            <xsd:complexType name="GetUserAuditLogsResponse">
                <xsd:sequence>
                    <xsd:element name="auditLogs" type="tns:ArrayOfAuditLog"/>
                    <xsd:element name="totalCount" type="xsd:int"/>
                    <xsd:element name="page" type="xsd:int"/>
                    <xsd:element name="pageSize" type="xsd:int"/>
                    <xsd:element name="success" type="xsd:boolean"/>
                    <xsd:element name="message" type="xsd:string"/>
                    <xsd:element name="timestamp" type="xsd:dateTime"/>
                </xsd:sequence>
            </xsd:complexType>

            <!-- Helper Types -->
            <xsd:complexType name="ArrayOfString">
                <xsd:sequence>
                    <xsd:element name="string" type="xsd:string" maxOccurs="unbounded" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>

        </xsd:schema>
    </wsdl:types>

    <!-- Messages Section -->
    <!-- Authentication Messages -->
    <wsdl:message name="RegisterUserRequest">
        <wsdl:part name="parameters" element="tns:RegisterUserRequest"/>
    </wsdl:message>

    <wsdl:message name="RegisterUserResponse">
        <wsdl:part name="parameters" element="tns:RegisterUserResponse"/>
    </wsdl:message>

    <wsdl:message name="AuthenticateUserRequest">
        <wsdl:part name="parameters" element="tns:AuthenticateUserRequest"/>
    </wsdl:message>

    <wsdl:message name="AuthenticateUserResponse">
        <wsdl:part name="parameters" element="tns:AuthenticateUserResponse"/>
    </wsdl:message>

    <wsdl:message name="LogoutUserRequest">
        <wsdl:part name="parameters" element="tns:LogoutUserRequest"/>
    </wsdl:message>

    <wsdl:message name="LogoutUserResponse">
        <wsdl:part name="parameters" element="tns:LogoutUserResponse"/>
    </wsdl:message>

    <!-- User Management Messages -->
    <wsdl:message name="GetUserProfileRequest">
        <wsdl:part name="parameters" element="tns:GetUserProfileRequest"/>
    </wsdl:message>

    <wsdl:message name="GetUserProfileResponse">
        <wsdl:part name="parameters" element="tns:GetUserProfileResponse"/>
    </wsdl:message>

    <wsdl:message name="UpdateUserProfileRequest">
        <wsdl:part name="parameters" element="tns:UpdateUserProfileRequest"/>
    </wsdl:message>

    <wsdl:message name="UpdateUserProfileResponse">
        <wsdl:part name="parameters" element="tns:UpdateUserProfileResponse"/>
    </wsdl:message>

    <wsdl:message name="GetAllUsersRequest">
        <wsdl:part name="parameters" element="tns:GetAllUsersRequest"/>
    </wsdl:message>

    <wsdl:message name="GetAllUsersResponse">
        <wsdl:part name="parameters" element="tns:GetAllUsersResponse"/>
    </wsdl:message>

    <wsdl:message name="DeactivateUserRequest">
        <wsdl:part name="parameters" element="tns:DeactivateUserRequest"/>
    </wsdl:message>

    <wsdl:message name="DeactivateUserResponse">
        <wsdl:part name="parameters" element="tns:DeactivateUserResponse"/>
    </wsdl:message>

    <!-- Role Management Messages -->
    <wsdl:message name="CreateRoleRequest">
        <wsdl:part name="parameters" element="tns:CreateRoleRequest"/>
    </wsdl:message>

    <wsdl:message name="CreateRoleResponse">
        <wsdl:part name="parameters" element="tns:CreateRoleResponse"/>
    </wsdl:message>

    <wsdl:message name="AssignRoleRequest">
        <wsdl:part name="parameters" element="tns:AssignRoleRequest"/>
    </wsdl:message>

    <wsdl:message name="AssignRoleResponse">
        <wsdl:part name="parameters" element="tns:AssignRoleResponse"/>
    </wsdl:message>

    <wsdl:message name="GetUserRolesRequest">
        <wsdl:part name="parameters" element="tns:GetUserRolesRequest"/>
    </wsdl:message>

    <wsdl:message name="GetUserRolesResponse">
        <wsdl:part name="parameters" element="tns:GetUserRolesResponse"/>
    </wsdl:message>

    <!-- Permission Management Messages -->
    <wsdl:message name="CreatePermissionRequest">
        <wsdl:part name="parameters" element="tns:CreatePermissionRequest"/>
    </wsdl:message>

    <wsdl:message name="CreatePermissionResponse">
        <wsdl:part name="parameters" element="tns:CreatePermissionResponse"/>
    </wsdl:message>

    <wsdl:message name="AssignPermissionToRoleRequest">
        <wsdl:part name="parameters" element="tns:AssignPermissionToRoleRequest"/>
    </wsdl:message>

    <wsdl:message name="AssignPermissionToRoleResponse">
        <wsdl:part name="parameters" element="tns:AssignPermissionToRoleResponse"/>
    </wsdl:message>

    <!-- Password Management Messages -->
    <wsdl:message name="RequestPasswordResetRequest">
        <wsdl:part name="parameters" element="tns:RequestPasswordResetRequest"/>
    </wsdl:message>

    <wsdl:message name="RequestPasswordResetResponse">
        <wsdl:part name="parameters" element="tns:RequestPasswordResetResponse"/>
    </wsdl:message>

    <wsdl:message name="ResetPasswordRequest">
        <wsdl:part name="parameters" element="tns:ResetPasswordRequest"/>
    </wsdl:message>

    <wsdl:message name="ResetPasswordResponse">
        <wsdl:part name="parameters" element="tns:ResetPasswordResponse"/>
    </wsdl:message>

    <wsdl:message name="ChangePasswordRequest">
        <wsdl:part name="parameters" element="tns:ChangePasswordRequest"/>
    </wsdl:message>

    <wsdl:message name="ChangePasswordResponse">
        <wsdl:part name="parameters" element="tns:ChangePasswordResponse"/>
    </wsdl:message>

    <!-- Audit Messages -->
    <wsdl:message name="GetAuditLogsRequest">
        <wsdl:part name="parameters" element="tns:GetAuditLogsRequest"/>
    </wsdl:message>

    <wsdl:message name="GetAuditLogsResponse">
        <wsdl:part name="parameters" element="tns:GetAuditLogsResponse"/>
    </wsdl:message>

    <wsdl:message name="GetUserAuditLogsRequest">
        <wsdl:part name="parameters" element="tns:GetUserAuditLogsRequest"/>
    </wsdl:message>

    <wsdl:message name="GetUserAuditLogsResponse">
        <wsdl:part name="parameters" element="tns:GetUserAuditLogsResponse"/>
    </wsdl:message>

    <!-- Port Types Section -->
    <wsdl:portType name="UserManagementPortType">

        <!-- Authentication Operations -->
        <wsdl:operation name="RegisterUser">
            <wsdl:input message="tns:RegisterUserRequest"/>
            <wsdl:output message="tns:RegisterUserResponse"/>
        </wsdl:operation>

        <wsdl:operation name="AuthenticateUser">
            <wsdl:input message="tns:AuthenticateUserRequest"/>
            <wsdl:output message="tns:AuthenticateUserResponse"/>
        </wsdl:operation>

        <wsdl:operation name="LogoutUser">
            <wsdl:input message="tns:LogoutUserRequest"/>
            <wsdl:output message="tns:LogoutUserResponse"/>
        </wsdl:operation>

        <!-- User Management Operations -->
        <wsdl:operation name="GetUserProfile">
            <wsdl:input message="tns:GetUserProfileRequest"/>
            <wsdl:output message="tns:GetUserProfileResponse"/>
        </wsdl:operation>

        <wsdl:operation name="UpdateUserProfile">
            <wsdl:input message="tns:UpdateUserProfileRequest"/>
            <wsdl:output message="tns:UpdateUserProfileResponse"/>
        </wsdl:operation>

        <wsdl:operation name="GetAllUsers">
            <wsdl:input message="tns:GetAllUsersRequest"/>
            <wsdl:output message="tns:GetAllUsersResponse"/>
        </wsdl:operation>

        <wsdl:operation name="DeactivateUser">
            <wsdl:input message="tns:DeactivateUserRequest"/>
            <wsdl:output message="tns:DeactivateUserResponse"/>
        </wsdl:operation>

        <!-- Role Management Operations -->
        <wsdl:operation name="CreateRole">
            <wsdl:input message="tns:CreateRoleRequest"/>
            <wsdl:output message="tns:CreateRoleResponse"/>
        </wsdl:operation>

        <wsdl:operation name="AssignRole">
            <wsdl:input message="tns:AssignRoleRequest"/>
            <wsdl:output message="tns:AssignRoleResponse"/>
        </wsdl:operation>

        <wsdl:operation name="GetUserRoles">
            <wsdl:input message="tns:GetUserRolesRequest"/>
            <wsdl:output message="tns:GetUserRolesResponse"/>
        </wsdl:operation>

        <!-- Permission Management Operations -->
        <wsdl:operation name="CreatePermission">
            <wsdl:input message="tns:CreatePermissionRequest"/>
            <wsdl:output message="tns:CreatePermissionResponse"/>
        </wsdl:operation>

        <wsdl:operation name="AssignPermissionToRole">
            <wsdl:input message="tns:AssignPermissionToRoleRequest"/>
            <wsdl:output message="tns:AssignPermissionToRoleResponse"/>
        </wsdl:operation>

        <!-- Password Management Operations -->
        <wsdl:operation name="RequestPasswordReset">
            <wsdl:input message="tns:RequestPasswordResetRequest"/>
            <wsdl:output message="tns:RequestPasswordResetResponse"/>
        </wsdl:operation>

        <wsdl:operation name="ResetPassword">
            <wsdl:input message="tns:ResetPasswordRequest"/>
            <wsdl:output message="tns:ResetPasswordResponse"/>
        </wsdl:operation>

        <wsdl:operation name="ChangePassword">
            <wsdl:input message="tns:ChangePasswordRequest"/>
            <wsdl:output message="tns:ChangePasswordResponse"/>
        </wsdl:operation>

        <!-- Audit Operations -->
        <wsdl:operation name="GetAuditLogs">
            <wsdl:input message="tns:GetAuditLogsRequest"/>
            <wsdl:output message="tns:GetAuditLogsResponse"/>
        </wsdl:operation>

        <wsdl:operation name="GetUserAuditLogs">
            <wsdl:input message="tns:GetUserAuditLogsRequest"/>
            <wsdl:output message="tns:GetUserAuditLogsResponse"/>
        </wsdl:operation>

    </wsdl:portType>

    <!-- Binding Section -->
    <wsdl:binding name="UserManagementSoapBinding" type="tns:UserManagementPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>

        <!-- Authentication Operations Binding -->
        <wsdl:operation name="RegisterUser">
            <soap:operation soapAction="http://example.com/usermanagement/RegisterUser"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="AuthenticateUser">
            <soap:operation soapAction="http://example.com/usermanagement/AuthenticateUser"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="LogoutUser">
            <soap:operation soapAction="http://example.com/usermanagement/LogoutUser"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <!-- User Management Operations Binding -->
        <wsdl:operation name="GetUserProfile">
            <soap:operation soapAction="http://example.com/usermanagement/GetUserProfile"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="UpdateUserProfile">
            <soap:operation soapAction="http://example.com/usermanagement/UpdateUserProfile"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="GetAllUsers">
            <soap:operation soapAction="http://example.com/usermanagement/GetAllUsers"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="DeactivateUser">
            <soap:operation soapAction="http://example.com/usermanagement/DeactivateUser"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <!-- Role Management Operations Binding -->
        <wsdl:operation name="CreateRole">
            <soap:operation soapAction="http://example.com/usermanagement/CreateRole"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="AssignRole">
            <soap:operation soapAction="http://example.com/usermanagement/AssignRole"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="GetUserRoles">
            <soap:operation soapAction="http://example.com/usermanagement/GetUserRoles"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <!-- Permission Management Operations Binding -->
        <wsdl:operation name="CreatePermission">
            <soap:operation soapAction="http://example.com/usermanagement/CreatePermission"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="AssignPermissionToRole">
            <soap:operation soapAction="http://example.com/usermanagement/AssignPermissionToRole"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <!-- Password Management Operations Binding -->
        <wsdl:operation name="RequestPasswordReset">
            <soap:operation soapAction="http://example.com/usermanagement/RequestPasswordReset"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="ResetPassword">
            <soap:operation soapAction="http://example.com/usermanagement/ResetPassword"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="ChangePassword">
            <soap:operation soapAction="http://example.com/usermanagement/ChangePassword"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <!-- Audit Operations Binding -->
        <wsdl:operation name="GetAuditLogs">
            <soap:operation soapAction="http://example.com/usermanagement/GetAuditLogs"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

        <wsdl:operation name="GetUserAuditLogs">
            <soap:operation soapAction="http://example.com/usermanagement/GetUserAuditLogs"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>

    </wsdl:binding>

    <!-- Service Section -->
    <wsdl:service name="UserManagementService">
        <wsdl:documentation>Enhanced User Management System SOAP API Service</wsdl:documentation>
        <wsdl:port name="UserManagementPort" binding="tns:UserManagementSoapBinding">
            <soap:address location="http://localhost:8000/soap"/>
        </wsdl:port>
    </wsdl:service>

</wsdl:definitions>"""
    
    return wsdl_content