# Claude Computer Use Agent - Complete System

> A scalable, session-based computer use agent system with real-time desktop control, MySQL persistence, and enhanced frontend with live VNC display.

## 🚀 Overview

This system transforms the original Anthropic Computer Use Demo into a production-ready, scalable architecture with:

- **FastAPI Backend**: Session management and real-time communication
- **MySQL Database**: Persistent storage for sessions and messages
- **Enhanced Frontend**: Modern interface with live desktop view
- **Real-time Desktop Control**: VNC integration for live agent observation
- **Docker Compose**: Complete containerized deployment

**Demo Video:** [Watch the system in action](https://drive.google.com/file/d/1kPIspffhSkKegO_JCKJ_FjYKmnmWBfTG/view?usp=sharing)

## 📋 Prerequisites

### System Requirements
- Docker and Docker Compose
- At least 4GB RAM
- 10GB free disk space
- Internet connection for API access

### API Key Setup
1. Get your Anthropic API key from [Anthropic Console](https://console.anthropic.com/)
2. Create the API key file:
   ```bash
   mkdir -p ~/.anthropic
   echo "your-api-key-here" > ~/.anthropic/api_key
   ```

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd computer-use-demo
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```bash
cat > .env << EOF
ANTHROPIC_API_KEY=your-api-key-here
API_PROVIDER=anthropic
EOF
```

### 3. Build and Start Services
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Verify Installation
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend accessibility
curl http://localhost:3000

# Check VNC service
curl http://localhost:6080/vnc.html
```

## 🌐 Access Points

### Primary Interfaces
- **Enhanced Frontend**: http://localhost:3000
  - Modern interface with live desktop view
  - Real-time chat and agent interaction
  - Session management and database integration

- **Original Streamlit**: http://localhost:8080
  - Original Anthropic demo interface
  - Combined desktop view and chat

### Additional Services
- **Backend API**: http://localhost:8000
  - RESTful API for session management
  - WebSocket endpoints for real-time updates
  - Health check: http://localhost:8000/health

- **VNC Desktop View**: http://localhost:6080/vnc.html
  - Direct access to desktop environment
  - Full VNC client interface

- **Streamlit Interface**: http://localhost:8501
  - Alternative Streamlit interface

- **MySQL Database**: localhost:3307
  - Database credentials: root/root1234
  - Database name: computer_use_demo

## 🏗️ Architecture

### Services Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Computer      │
│   (Nginx)       │◄──►│   (FastAPI)     │◄──►│   Use Demo      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MySQL         │
                       │   Port: 3307    │
                       └─────────────────┘
```

### Key Components

1. **Frontend Service** (`frontend/`)
   - Nginx-based static file server
   - Enhanced HTML/JS interface
   - Real-time WebSocket communication
   - Live VNC desktop view integration

2. **Backend Service** (`backend/`)
   - FastAPI application
   - Session management
   - MySQL database integration
   - Agent execution coordination
   - WebSocket real-time updates

3. **Computer Use Demo** (`computer_use_demo/`)
   - Original Anthropic agent
   - Desktop environment with Xvfb
   - Screenshot and control tools
   - Streamlit interface

4. **MySQL Database** (`mysql/`)
   - Persistent session storage
   - Message history
   - Tool results and screenshots

## 🔧 Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=your-api-key-here
API_PROVIDER=anthropic

# Database (optional - defaults provided)
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root1234
MYSQL_DATABASE=computer_use_demo
```

### Database Schema
```sql
-- Sessions table
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status ENUM('idle', 'running', 'completed', 'error') DEFAULT 'idle',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'tool', 'system') NOT NULL,
    content TEXT NOT NULL,
    message_type ENUM('text', 'tool_result', 'screenshot', 'error') DEFAULT 'text',
    tool_name VARCHAR(255),
    screenshot LONGTEXT,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

## 🚀 Usage

### Starting the System
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Managing Individual Services
```bash
# Restart backend
docker-compose restart backend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check backend logs
docker-compose logs backend

# Access backend shell
docker-compose exec backend bash
```

### Database Operations
```bash
# Access MySQL
docker-compose exec mysql mysql -u root -proot1234

# Backup database
docker-compose exec mysql mysqldump -u root -proot1234 computer_use_demo > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u root -proot1234 computer_use_demo < backup.sql
```

## 📡 API Endpoints

### Session Management
```bash
# Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "My Session", "initial_message": "Hello"}'

# List sessions
curl http://localhost:8000/sessions

# Get session details
curl http://localhost:8000/sessions/{session_id}

# Send message
curl -X POST http://localhost:8000/sessions/{session_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Take a screenshot"}'
```

### WebSocket Connection
```javascript
// Connect to real-time updates
const ws = new WebSocket(`ws://localhost:8000/sessions/{session_id}/stream`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Authentication Error**
   ```bash
   # Verify API key file exists
   ls -la ~/.anthropic/api_key
   
   # Check API key content
   cat ~/.anthropic/api_key
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :8000
   lsof -i :3000
   lsof -i :3307
   
   # Stop conflicting services
   sudo lsof -ti:8000 | xargs kill -9
   ```

3. **Database Connection Issues**
   ```bash
   # Check MySQL container
   docker-compose logs mysql
   
   # Restart MySQL
   docker-compose restart mysql
   ```

4. **Agent Execution Problems**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Test agent directly
   docker-compose exec computer-use-demo python test_agent.py
   ```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend accessibility
curl http://localhost:3000

# VNC service
curl http://localhost:6080/vnc.html

# Database connection
docker-compose exec backend python backend/test_db.py
```

## 📊 Monitoring

### Service Status
```bash
# View all services
docker-compose ps

# Check resource usage
docker stats

# View service logs
docker-compose logs -f [service_name]
```

### Database Monitoring
```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -proot1234 computer_use_demo

# Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'computer_use_demo';
```

## 🔒 Security Considerations

1. **API Key Protection**
   - Store API key in `~/.anthropic/api_key`
   - Never commit API keys to version control
   - Use environment variables in production

2. **Network Security**
   - Services are exposed on localhost only
   - Use reverse proxy for external access
   - Implement proper authentication for production

3. **Database Security**
   - Change default MySQL passwords
   - Restrict database access
   - Regular backups

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
export ANTHROPIC_API_KEY="your-production-api-key"
export MYSQL_PASSWORD="strong-production-password"
export NODE_ENV=production
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

## 📝 Development

### Local Development
```bash
# Mount source code for development
docker-compose -f docker-compose.dev.yml up -d

# Run tests
docker-compose exec backend python -m pytest

# Code formatting
docker-compose exec backend black backend/
```

### Adding New Features
1. Modify backend code in `backend/`
2. Update frontend in `frontend/`
3. Rebuild affected services
4. Test thoroughly

## 📚 Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎯 Quick Start Summary

1. **Setup**: `git clone && cd computer-use-demo`
2. **Configure**: Create `~/.anthropic/api_key` with your API key
3. **Start**: `docker-compose up -d`
4. **Access**: Open http://localhost:3000
5. **Test**: Send a message like "Take a screenshot"

**All services will be available at:**
- Enhanced Frontend: http://localhost:3000
- Original Streamlit: http://localhost:8080
- Backend API: http://localhost:8000
- VNC Desktop: http://localhost:6080/vnc.html
- MySQL Database: localhost:3307

The system is now ready for production use with full computer control capabilities! 🚀 
