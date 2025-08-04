"""
FastAPI Backend for Claude Computer Use Agent Session Management
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session

# Import the real Claude agent components
from computer_use_demo.loop import APIProvider, sampling_loop
from computer_use_demo.tools import ToolResult, ToolVersion

# Import database models
from backend.database import get_db, Session as DBSession, Message as DBMessage, init_db

app = FastAPI(
    title="Claude Computer Use Agent API",
    description="Backend API for managing computer use agent sessions",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections (still in-memory for real-time)
active_connections: Dict[str, List[WebSocket]] = {}

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: str = "text"  # text, tool_result, screenshot, error
    tool_name: Optional[str] = None
    screenshot: Optional[str] = None  # base64 encoded image
    error: Optional[str] = None

class Session(BaseModel):
    id: str
    name: str
    messages: List[Message] = []
    status: str = "idle"  # idle, running, completed, error
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CreateSessionRequest(BaseModel):
    name: str
    initial_message: Optional[str] = None

class SendMessageRequest(BaseModel):
    message: str

class SessionResponse(BaseModel):
    id: str
    name: str
    status: str
    message_count: int
    created_at: datetime
    updated_at: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    return {"message": "Claude Computer Use Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Create a new agent session"""
    session_id = str(uuid.uuid4())
    
    # Create session in database
    db_session = DBSession(
        id=session_id,
        name=request.name,
        status="idle"
    )
    db.add(db_session)
    
    # Add initial message if provided
    if request.initial_message:
        db_message = DBMessage(
            session_id=session_id,
            role="user",
            content=request.initial_message,
            message_type="text"
        )
        db.add(db_message)
    
    db.commit()
    db.refresh(db_session)
    
    # Initialize WebSocket connections
    active_connections[session_id] = []
    
    return SessionResponse(
        id=session_id,
        name=db_session.name,
        status=db_session.status,
        message_count=len(db_session.messages),
        created_at=db_session.created_at,
        updated_at=db_session.updated_at
    )

@app.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(db: Session = Depends(get_db)):
    """List all sessions"""
    db_sessions = db.query(DBSession).all()
    
    return [
        SessionResponse(
            id=session.id,
            name=session.name,
            status=session.status,
            message_count=len(session.messages),
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        for session in db_sessions
    ]

@app.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get session details and messages"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Convert database messages to Pydantic models
    messages = []
    for db_message in db_session.messages:
        message = Message(
            role=db_message.role,
            content=db_message.content,
            timestamp=db_message.timestamp,
            message_type=db_message.message_type,
            tool_name=db_message.tool_name,
            screenshot=db_message.screenshot,
            error=db_message.error
        )
        messages.append(message)
    
    return Session(
        id=db_session.id,
        name=db_session.name,
        status=db_session.status,
        messages=messages,
        created_at=db_session.created_at,
        updated_at=db_session.updated_at
    )

@app.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, request: SendMessageRequest, db: Session = Depends(get_db)):
    """Send a message to an active session"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Add user message to database
    db_message = DBMessage(
        session_id=session_id,
        role="user",
        content=request.message,
        message_type="text"
    )
    db.add(db_message)
    
    # Update session status
    db_session.status = "running"
    db_session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_session)
    
    # Notify connected clients about user message
    await broadcast_to_session(session_id, {
        "type": "message",
        "role": "user",
        "content": request.message,
        "timestamp": db_message.timestamp.isoformat()
    })
    
    # Process with real Claude agent
    await process_with_real_agent(db_session, request.message, db)
    
    return {"status": "message sent", "session_id": session_id}

@app.websocket("/sessions/{session_id}/stream")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    await websocket.accept()
    
    if session_id not in active_connections:
        active_connections[session_id] = []
    
    active_connections[session_id].append(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        if session_id in active_connections:
            active_connections[session_id].remove(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]

def safe_encode_content(content):
    """Safely encode content to handle UTF-8 issues"""
    if isinstance(content, bytes):
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('utf-8', errors='replace')
    return str(content)

async def process_with_real_agent(db_session: DBSession, user_message: str, db: Session):
    """Process user message with real Claude agent"""
    try:
        # Convert session messages to Claude format
        messages = []
        for db_message in db_session.messages:
            messages.append({
                "role": db_message.role,
                "content": [{"type": "text", "text": db_message.content}]
            })
        
        # Execute the agent in the computer-use-demo container where desktop environment is available
        import subprocess
        import json
        
        # Use the existing test_agent.py file and pass the message as environment variable
        result = subprocess.run([
            "docker", "exec", "-e", f"AGENT_MESSAGE={user_message}", "computer-use-demo", 
            "python", "/home/computeruse/test_agent.py"
        ], capture_output=True, text=True)
            
        # Process the output
        for line in result.stdout.split('\n'):
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get('type') == 'output':
                        # Save assistant message
                        db_message = DBMessage(
                            session_id=db_session.id,
                            role="assistant",
                            content=data['content'],
                            message_type="text"
                        )
                        db.add(db_message)
                        db.commit()
                        
                        # Broadcast to clients
                        await broadcast_to_session(db_session.id, {
                            "type": "message",
                            "role": "assistant",
                            "content": data['content'],
                            "timestamp": db_message.timestamp.isoformat()
                        })
                    
                    elif data.get('type') == 'tool_output':
                        # Save tool output
                        safe_content = safe_encode_content(data.get('output', ''))
                        safe_error = safe_encode_content(data.get('error')) if data.get('error') else None
                        
                        db_message = DBMessage(
                            session_id=db_session.id,
                            role="tool",
                            content=safe_content,
                            message_type="tool_result",
                            tool_name=data.get('tool_id'),
                            error=safe_error
                        )
                        db.add(db_message)
                        db.commit()
                        
                        # Broadcast to clients
                        await broadcast_to_session(db_session.id, {
                            "type": "tool_result",
                            "role": "tool",
                            "content": db_message.content,
                            "tool_name": db_message.tool_name,
                            "error": db_message.error,
                            "timestamp": db_message.timestamp.isoformat()
                        })
                    
                    elif data.get('type') == 'api_error':
                        # Save error
                        db_message = DBMessage(
                            session_id=db_session.id,
                            role="system",
                            content=f"API Error: {data['error']}",
                            message_type="error",
                            error=data['error']
                        )
                        db.add(db_message)
                        db.commit()
                        
                        # Broadcast to clients
                        await broadcast_to_session(db_session.id, {
                            "type": "error",
                            "role": "system",
                            "content": db_message.content,
                            "timestamp": db_message.timestamp.isoformat()
                        })
                        
                except json.JSONDecodeError:
                    # Skip non-JSON lines
                    continue
                except Exception as e:
                    print(f"Error processing agent output: {e}")
            
            # Check for errors
            if result.stderr:
                print(f"Agent execution stderr: {result.stderr}")
        
        # Update session status
        db_session.status = "idle"
        db_session.updated_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # Update session status to error
        db_session.status = "error"
        db_session.updated_at = datetime.utcnow()
        
        # Save error message to database
        error_content = f"Error processing message: {str(e)}"
        try:
            error_content = safe_encode_content(error_content)
        except:
            error_content = "Error processing message: Unknown error"
            
        db_message = DBMessage(
            session_id=db_session.id,
            role="system",
            content=error_content,
            message_type="error",
            error=str(e)
        )
        db.add(db_message)
        db.commit()
        
        # Notify connected clients about error
        await broadcast_to_session(db_session.id, {
            "type": "error",
            "role": "system",
            "content": db_message.content,
            "timestamp": db_message.timestamp.isoformat()
        })

async def broadcast_to_session(session_id: str, message: dict):
    """Broadcast message to all connected clients for a session"""
    if session_id in active_connections:
        disconnected = []
        for websocket in active_connections[session_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            active_connections[session_id].remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 