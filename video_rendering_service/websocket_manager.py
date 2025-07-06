"""
🔗 WebSocket Manager for Real-time Communication

Handles WebSocket connections for live progress updates and notifications.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_data[websocket] = {
            "connected_at": asyncio.get_event_loop().time(),
            "messages_sent": 0,
            "client_id": id(websocket)
        }
        logger.info(f"WebSocket client connected: {id(websocket)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_data:
                del self.connection_data[websocket]
            logger.info(f"WebSocket client disconnected: {id(websocket)}")
    
    async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific WebSocket client"""
        try:
            await websocket.send_text(json.dumps(message))
            if websocket in self.connection_data:
                self.connection_data[websocket]["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Failed to send message to client {id(websocket)}: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected_clients = []
        
        for websocket in self.active_connections.copy():
            try:
                await websocket.send_text(message_text)
                if websocket in self.connection_data:
                    self.connection_data[websocket]["messages_sent"] += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to client {id(websocket)}: {e}")
                disconnected_clients.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket)
    
    async def send_progress_update(self, job_id: str, progress: float, status: str):
        """Send progress update for specific job"""
        message = {
            "type": "progress_update",
            "job_id": job_id,
            "progress": progress,
            "status": status,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)
    
    async def send_job_completed(self, job_id: str, success: bool, message: str = ""):
        """Send job completion notification"""
        notification = {
            "type": "job_completed",
            "job_id": job_id,
            "success": success,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(notification)
    
    async def send_system_stats(self, stats: Dict[str, Any]):
        """Send system performance statistics"""
        message = {
            "type": "system_stats",
            "data": stats,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)
    
    async def disconnect_all(self):
        """Disconnect all WebSocket clients"""
        for websocket in self.active_connections.copy():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {e}")
            finally:
                self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_messages = sum(
            data.get("messages_sent", 0) 
            for data in self.connection_data.values()
        )
        
        return {
            "active_connections": len(self.active_connections),
            "total_messages_sent": total_messages,
            "connections": [
                {
                    "client_id": data["client_id"],
                    "connected_at": data["connected_at"],
                    "messages_sent": data["messages_sent"]
                }
                for data in self.connection_data.values()
            ]
        }