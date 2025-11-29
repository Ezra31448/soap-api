"""
Audit service for Enhanced User Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

from src.database.connection import get_database_session
from src.models.audit_log import AuditLog

logger = structlog.get_logger()


class AuditService:
    """Service for handling audit operations"""
    
    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
    
    async def log_event(self, user_id: int = None, action: str = "", 
                      resource_type: str = "", resource_id: int = None,
                      old_values: Dict[str, Any] = None, 
                      new_values: Dict[str, Any] = None,
                      ip_address: str = None, user_agent: str = None) -> int:
        """
        Log an audit event
        """
        async with get_database_session() as session:
            try:
                # Create audit log
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    old_values=str(old_values) if old_values else None,
                    new_values=str(new_values) if new_values else None,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                session.add(audit_log)
                await session.flush()  # Get the ID
                
                audit_id = audit_log.id
                await session.commit()
                
                self.logger.info("Audit event logged", 
                              audit_id=audit_id,
                              user_id=user_id,
                              action=action,
                              resource_type=resource_type,
                              resource_id=resource_id)
                
                return audit_id
                
            except Exception as e:
                await session.rollback()
                self.logger.error("Failed to log audit event", error=str(e))
                raise
    
    async def get_audit_logs(self, user_id: int = None, action: str = None,
                          resource_type: str = None, start_date: datetime = None,
                          end_date: datetime = None, page: int = 1,
                          page_size: int = 20) -> Dict[str, Any]:
        """
        Get audit logs with filtering and pagination
        """
        async with get_database_session() as session:
            try:
                # Build query with filters
                query = AuditLog.build_query(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Get total count
                count_query = AuditLog.build_count_query(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    start_date=start_date,
                    end_date=end_date
                )
                total_count = await session.scalar(count_query)
                
                # Apply pagination
                offset = (page - 1) * page_size
                query = query.offset(offset).limit(page_size)
                query = query.order_by(AuditLog.created_at.desc())
                
                result = await session.execute(query)
                audit_logs = list(result.scalars().all())
                
                # Format audit log data
                audit_log_list = []
                for audit_log in audit_logs:
                    log_data = {
                        "audit_id": audit_log.id,
                        "user_id": audit_log.user_id,
                        "action": audit_log.action,
                        "resource_type": audit_log.resource_type,
                        "resource_id": audit_log.resource_id,
                        "old_values": audit_log.old_values,
                        "new_values": audit_log.new_values,
                        "ip_address": audit_log.ip_address,
                        "user_agent": audit_log.user_agent,
                        "created_at": audit_log.created_at.isoformat()
                    }
                    audit_log_list.append(log_data)
                
                self.logger.info("Audit logs retrieved", 
                              user_id=user_id,
                              page=page,
                              page_size=page_size,
                              total_count=total_count)
                
                return {
                    "audit_logs": audit_log_list,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
                
            except Exception as e:
                self.logger.error("Get audit logs failed", error=str(e))
                raise
    
    async def get_user_audit_logs(self, target_user_id: int, page: int = 1,
                                page_size: int = 20, start_date: datetime = None,
                                end_date: datetime = None) -> Dict[str, Any]:
        """
        Get audit logs for a specific user
        """
        return await self.get_audit_logs(
            user_id=target_user_id,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_audit_log_by_id(self, audit_id: int) -> Dict[str, Any]:
        """
        Get a specific audit log by ID
        """
        async with get_database_session() as session:
            try:
                # Get audit log
                audit_log = await AuditLog.find_by_id(session, audit_id)
                if not audit_log:
                    raise NotFoundError("Audit log not found")
                
                self.logger.info("Audit log retrieved", audit_id=audit_id)
                
                return {
                    "audit_id": audit_log.id,
                    "user_id": audit_log.user_id,
                    "action": audit_log.action,
                    "resource_type": audit_log.resource_type,
                    "resource_id": audit_log.resource_id,
                    "old_values": audit_log.old_values,
                    "new_values": audit_log.new_values,
                    "ip_address": audit_log.ip_address,
                    "user_agent": audit_log.user_agent,
                    "created_at": audit_log.created_at.isoformat()
                }
                
            except Exception as e:
                self.logger.error("Get audit log failed", error=str(e))
                raise
    
    async def get_audit_statistics(self, start_date: datetime = None,
                               end_date: datetime = None) -> Dict[str, Any]:
        """
        Get audit statistics
        """
        async with get_database_session() as session:
            try:
                # Build base query with date filters
                base_query = AuditLog.build_query(
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Total audit events
                total_events = await session.scalar(
                    AuditLog.build_count_query(
                        start_date=start_date,
                        end_date=end_date
                    )
                )
                
                # Events by action
                events_by_action = await session.execute(
                    base_query.with_entities(
                        AuditLog.action,
                        AuditLog.id.label('count')
                    )
                    .group_by(AuditLog.action)
                    .order_by(AuditLog.id.desc())
                )
                action_counts = [
                    {
                        "action": row.action,
                        "count": row.count
                    }
                    for row in events_by_action.all()
                ]
                
                # Events by resource type
                events_by_resource = await session.execute(
                    base_query.with_entities(
                        AuditLog.resource_type,
                        AuditLog.id.label('count')
                    )
                    .group_by(AuditLog.resource_type)
                    .order_by(AuditLog.id.desc())
                )
                resource_counts = [
                    {
                        "resource_type": row.resource_type,
                        "count": row.count
                    }
                    for row in events_by_resource.all()
                ]
                
                # Recent events (last 24 hours)
                twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
                recent_events = await session.scalar(
                    AuditLog.build_count_query(
                        start_date=twenty_four_hours_ago
                    )
                )
                
                # Top users by activity
                top_users = await session.execute(
                    base_query.with_entities(
                        AuditLog.user_id,
                        AuditLog.id.label('count')
                    )
                    .where(AuditLog.user_id.isnot(None))
                    .group_by(AuditLog.user_id)
                    .order_by(AuditLog.id.desc())
                    .limit(10)
                )
                
                self.logger.info("Audit statistics retrieved")
                
                return {
                    "total_events": total_events,
                    "events_by_action": action_counts,
                    "events_by_resource_type": resource_counts,
                    "recent_events_24h": recent_events,
                    "top_active_users": [
                        {
                            "user_id": row.user_id,
                            "event_count": row.count
                        }
                        for row in top_users.all()
                    ]
                }
                
            except Exception as e:
                self.logger.error("Get audit statistics failed", error=str(e))
                raise
    
    async def export_audit_logs(self, format: str = "json", user_id: int = None,
                             start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Export audit logs in specified format
        """
        try:
            # Get audit logs
            audit_data = await self.get_audit_logs(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                page=1,
                page_size=10000  # Large page size for export
            )
            
            # Format based on requested format
            if format.lower() == "csv":
                # Convert to CSV format
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    "Audit ID", "User ID", "Action", "Resource Type", 
                    "Resource ID", "Old Values", "New Values",
                    "IP Address", "User Agent", "Created At"
                ])
                
                # Write data
                for log in audit_data["audit_logs"]:
                    writer.writerow([
                        log["audit_id"],
                        log["user_id"],
                        log["action"],
                        log["resource_type"],
                        log["resource_id"],
                        log["old_values"],
                        log["new_values"],
                        log["ip_address"],
                        log["user_agent"],
                        log["created_at"]
                    ])
                
                content = output.getvalue()
                content_type = "text/csv"
                filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                
            else:
                # Default to JSON format
                import json
                content = json.dumps(audit_data, indent=2)
                content_type = "application/json"
                filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            self.logger.info("Audit logs exported", 
                          format=format,
                          user_id=user_id,
                          record_count=len(audit_data["audit_logs"]))
            
            return {
                "content": content,
                "content_type": content_type,
                "filename": filename,
                "record_count": len(audit_data["audit_logs"])
            }
            
        except Exception as e:
            self.logger.error("Export audit logs failed", error=str(e))
            raise