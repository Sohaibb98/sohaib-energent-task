# Claude Computer Use Agent - Backend API

A scalable backend system for managing Claude Computer Use Agent sessions with real-time capabilities, built on top of the existing Anthropic Computer Use Demo.

## 🚀 Features

- **Session Management**: Create and manage multiple agent sessions
- **Real-time Communication**: WebSocket streaming for live updates
- **VNC Integration**: Direct access to virtual machine desktop
- **RESTful API**: Clean FastAPI backend with comprehensive endpoints
- **Docker Compose**: Easy local development and deployment
- **Simple Frontend**: HTML/JS demo interface

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │ Computer Use    │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   Demo          │
│                 │    │                 │    │ (Port 8080)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   VNC Server    │
                       │   (Port 6080)   │
                       └─────────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Anthropic API key
- Git

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd computer-use-demo

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. Start the Services

```bash
# Start all services with Docker Compose
docker-compose up --build
```

### 3. Access the Application

- **Frontend Demo**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **VNC Viewer**: http://localhost:6080/vnc.html
- **Original Streamlit**: http://localhost:8080

## 🔧 API Endpoints

### Sessions

- `GET /sessions` - List all sessions
- `POST /sessions` - Create new session
- `GET /sessions/{session_id}` - Get session details
- `POST /sessions/{session_id}/messages` - Send message to session

### Real-time

- `WS /sessions/{session_id}/stream` - WebSocket for real-time updates

### Health

- `GET /health` - Health check endpoint

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html          # Simple HTML demo
├── computer_use_demo/      # Original Anthropic demo
├── docker-compose.yml      # Multi-service setup
├── Dockerfile.backend      # Backend container
└── README_NEW.md          # This file
```

## 🔄 Development Workflow

### Backend Development

```bash
# Run backend locally
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Serve frontend locally
cd frontend
python -m http.server 3000
```

### Docker Development

```bash
# Rebuild and restart specific service
docker-compose up --build backend

# View logs
docker-compose logs -f backend

# Access container shell
docker-compose exec backend bash
```

## 🧪 Testing the API

### Create a Session

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Session", "initial_message": "Hello!"}'
```

### Send a Message

```bash
curl -X POST "http://localhost:8000/sessions/{session_id}/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "Take a screenshot"}'
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/sessions/{session_id}/stream');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## 🔒 Security Considerations

- **API Key Management**: Store API keys securely using environment variables
- **CORS Configuration**: Configure allowed origins for production
- **Rate Limiting**: Implement rate limiting for API endpoints
- **Input Validation**: All inputs are validated using Pydantic models

## 🚀 Production Deployment

### Environment Variables

```bash
ANTHROPIC_API_KEY=your-api-key
API_PROVIDER=anthropic  # or bedrock, vertex
WIDTH=1024
HEIGHT=768
```

### Database Integration

For production, replace the in-memory storage with a proper database:

```python
# Example with SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:password@localhost/dbname")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Reverse Proxy

Use Nginx or similar for production:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
    }
    
    location /ws/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 Monitoring

### Health Checks

- Backend: `GET /health`
- Docker: Built-in health checks in Dockerfile.backend

### Logging

```bash
# View application logs
docker-compose logs -f backend

# View VNC logs
docker-compose logs -f computer-use-demo
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 3000, 8000, 8080, 6080 are available
2. **API Key Issues**: Verify ANTHROPIC_API_KEY is set correctly
3. **VNC Connection**: Check if VNC server is running on port 6080
4. **WebSocket Issues**: Ensure WebSocket connections are properly configured

### Debug Mode

```bash
# Run with debug logging
docker-compose up --build -d
docker-compose logs -f backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is based on the Anthropic Computer Use Demo and follows the same license terms.

## 🙏 Acknowledgments

- Anthropic for the original Computer Use Demo
- FastAPI for the excellent web framework
- Docker for containerization
- noVNC for web-based VNC access 