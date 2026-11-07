"""WebSocket Handler for Real-Time Agent Communication

Provides real-time bi-directional communication between the FastAPI backend
and the frontend, enabling agents to push updates to connected clients.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time agent communication."""
    
    def __init__(self):
        # Connections organized by agent name
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "Nexus": set(),
            "Radarito": set(), 
            "Cerebrito": set(),
            "Centinela": set(),
            "Mensajerito": set(),
            "Auditor": set(),
        }
        # Broadcast channels for inter-agent communication
        self.broadcast_channels: Dict[str, Set[WebSocket]] = set()
        self.client_agent_map: Dict[WebSocket, str] = {}  # client -> current agent
    
    async def connect(self, websocket: WebSocket, agent_name: str = "Nexus") -> None:
        """Accept a new WebSocket connection for a specific agent."""
        await websocket.accept()
        self.active_connections[agent_name].add(websocket)
        self.client_agent_map[websocket] = agent_name
        logger.info(f"WebSocket connected: {agent_name}, total connections: {len(self.active_connections[agent_name])}")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        agent_name = self.client_agent_map.pop(websocket, "Nexus")
        for agent_list in self.active_connections.values():
            agent_list.discard(websocket)
        logger.info(f"WebSocket disconnected: {agent_name}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_agent(self, agent_name: str, message: dict) -> None:
        """Broadcast a message to all clients connected to a specific agent."""
        if agent_name in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[agent_name]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {agent_name}: {e}")
                    disconnected.add(connection)
            # Remove disconnected clients
            self.active_connections[agent_name] -= disconnected
    
    async def broadcast_to_all(self, message: dict) -> None:
        """Broadcast a message to all connected clients."""
        disconnected = set()
        for agent_name, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error in broadcast: {e}")
                    disconnected.add(connection)
        
        # Clean up disconnected clients across all agents
        for agent_name, connections in self.active_connections.items():
            self.active_connections[agent_name] -= disconnected
    
    async def send_agent_output(self, agent_name: str, output: dict, output_type: str = "general") -> None:
        """Send agent output to connected clients with audit information."""
        message = {
            "type": "agent_output",
            "agent": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "output": output,
            "output_type": output_type,
            "status": "delivered",
        }
        await self.broadcast_to_agent(agent_name, message)


# Global manager instance
manager = ConnectionManager()


# WebSocket endpoints for each agent
async def nexus_websocket(websocket: WebSocket):
    """WebSocket endpoint for Nexus - the central orchestrator."""
    await manager.connect(websocket, "Nexus")
    try:
        while True:
            data = await websocket.receive_json()
            # Handle Nexus routing commands
            message_type = data.get("type", "chat")
            if message_type == "route":
                intent = data.get("intent", "TECHNICAL_PROFILE")
                target = data.get("target", "Cerebrito")
                output = await manager.broadcast_to_agent(target, {
                    "intent": intent,
                    "routed_from": "Nexus",
                    "status": "pending",
                })
            elif message_type == "session":
                action = data.get("action", "status")
                output = await manager.broadcast_to_agent("Nexus", {
                    "action": action,
                    "status": "acknowledged",
                })
            else:
                # Default: chat message routing
                output = await manager.broadcast_to_agent("Cerebrito", {
                    "message": data.get("message", ""),
                    "source": "Nexus WebSocket",
                    "status": "received",
                })
                await manager.send_personal_message(output, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def radarito_websocket(websocket: WebSocket):
    """WebSocket endpoint for Radarito - news curation."""
    await manager.connect(websocket, "Radarito")
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "fetch_news":
                category = data.get("category", "AI_SOFTWARE")
                output = await manager.broadcast_to_agent("Radarito", {
                    "type": "news_fetch",
                    "category": category,
                    "status": "initiated",
                })
            await manager.send_personal_message(output, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def cerebrito_websocket(websocket: WebSocket):
    """WebSocket endpoint for Cerebrito - RAG technical queries."""
    await manager.connect(websocket, "Cerebrito")
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "query":
                question = data.get("question", "")
                output = await manager.broadcast_to_agent("Cerebrito", {
                    "type": "rag_query",
                    "question": question,
                    "status": "processing",
                })
                await manager.send_personal_message(output, websocket)
            elif data.get("type") == "feedback":
                # User feedback on answer quality
                feedback = data.get("feedback", "neutral")
                output = await manager.broadcast_to_agent("Cerebrito", {
                    "type": "feedback_received",
                    "feedback": feedback,
                    "status": "recorded",
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def centinela_websocket(websocket: WebSocket):
    """WebSocket endpoint for Centinela - security guardrails."""
    await manager.connect(websocket, "Centinela")
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "evaluate":
                prompt = data.get("prompt", "")
                output = await manager.broadcast_to_agent("Centinela", {
                    "type": "safety_evaluation",
                    "prompt": prompt,
                    "status": "evaluating",
                })
                await manager.send_personal_message(output, websocket)
            elif data.get("type") == "verdict":
                # Receive verdict from client
                verdict = data.get("verdict", "")
                output = await manager.broadcast_to_agent("Centinela", {
                    "type": "verdict_recorded",
                    "verdict": verdict,
                    "status": "accepted",
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def mensajerito_websocket(websocket: WebSocket):
    """WebSocket endpoint for Mensajerito - lead triage."""
    await manager.connect(websocket, "Mensajerito")
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "evaluate_lead":
                transcript = data.get("transcript", "")
                output = await manager.broadcast_to_agent("Mensajerito", {
                    "type": "lead_evaluation",
                    "transcript": transcript,
                    "status": "processing",
                })
                await manager.send_personal_message(output, websocket)
            elif data.get("type") == "dispatch":
                # Dispatch lead notification
                lead_data = data.get("lead_data", {})
                output = await manager.broadcast_to_agent("Mensajerito", {
                    "type": "lead_dispatched",
                    "lead_data": lead_data,
                    "status": "queued",
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def auditor_websocket(websocket: WebSocket):
    """WebSocket endpoint for Auditor - binary QA gate."""
    await manager.connect(websocket, "Auditor")
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "audit":
                output_data = data.get("output_data", {})
                output = await manager.broadcast_to_agent("Auditor", {
                    "type": "audit_execution",
                    "output_data": output_data,
                    "status": "analyzing",
                })
                await manager.send_personal_message(output, websocket)
            elif data.get("type") == "verdict":
                audit_verdict = data.get("verdict", "")
                output = await manager.broadcast_to_agent("Auditor", {
                    "type": "audit_verdict_recorded",
                    "verdict": audit_verdict,
                    "status": "recorded",
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# FastAPI endpoint handlers
async def websocket_route(websocket: WebSocket, agent_name: str):
    """Route WebSocket connections to the appropriate agent handler."""
    handlers = {
        "Nexus": nexus_websocket,
        "Radarito": radarito_websocket,
        "Cerebrito": cerebrito_websocket,
        "Centinela": centinela_websocket,
        "Mensajerito": mensajerito_websocket,
        "Auditor": auditor_websocket,
    }
    
    handler = handlers.get(agent_name, nexus_websocket)
    await handler(websocket)


# Health check endpoint for WebSocket connections
async def websocket_status() -> dict:
    """Return WebSocket connection status."""
    total = sum(len(connections) for connections in manager.active_connections.values())
    return {
        "status": "operational",
        "total_connections": total,
        "agents": {name: len(conns) for name, conns in manager.active_connections.items()},
        "timestamp": asyncio.get_event_loop().time(),
    }