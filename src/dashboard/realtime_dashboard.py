from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket
from dataclasses import dataclass
import asyncio
import json
from datetime import datetime

@dataclass
class DashboardConfig:
    update_interval: int
    max_connections: int
    cache_duration: int

class RealtimeDashboard:
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.active_connections = {}
        self.data_cache = {}
        self.last_updates = {}
        
    async def connect_client(self,
                           websocket: WebSocket,
                           client_id: str,
                           client_type: str) -> None:
        """Handle new dashboard connection"""
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "type": client_type,
            "subscriptions": []
        }
        
    async def subscribe_to_updates(self,
                                 client_id: str,
                                 topics: List[str]) -> None:
        """Subscribe client to real-time updates"""
        if client_id in self.active_connections:
            self.active_connections[client_id]["subscriptions"].extend(topics)
            
    async def broadcast_update(self,
                             topic: str,
                             data: Dict[str, Any]) -> None:
        """Broadcast updates to subscribed clients"""
        for client_id, connection in self.active_connections.items():
            if topic in connection["subscriptions"]:
                try:
                    await connection["websocket"].send_json({
                        "topic": topic,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    await self._handle_connection_error(client_id, e)

    async def connect(self, websocket: WebSocket, 