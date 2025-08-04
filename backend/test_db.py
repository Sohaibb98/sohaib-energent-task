"""
Database test script for MySQL integration
"""

import os
import sys
from datetime import datetime
from database import SessionLocal, Session as DBSession, Message as DBMessage

def test_database_connection():
    """Test database connection and basic operations"""
    try:
        # Test connection
        db = SessionLocal()
        print("✅ Database connection successful!")
        
        # Test creating a session
        test_session = DBSession(
            id="test-session-123",
            name="Test Session",
            status="idle"
        )
        db.add(test_session)
        
        # Test creating a message
        test_message = DBMessage(
            session_id="test-session-123",
            role="user",
            content="Hello, this is a test message!",
            message_type="text"
        )
        db.add(test_message)
        
        # Commit changes
        db.commit()
        print("✅ Database write operations successful!")
        
        # Test reading
        session = db.query(DBSession).filter(DBSession.id == "test-session-123").first()
        if session:
            print(f"✅ Database read operations successful! Found session: {session.name}")
            print(f"   Session has {len(session.messages)} messages")
        
        # Clean up test data
        db.delete(test_session)
        db.commit()
        print("✅ Database cleanup successful!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing MySQL database integration...")
    success = test_database_connection()
    if success:
        print("🎉 All database tests passed!")
        sys.exit(0)
    else:
        print("💥 Database tests failed!")
        sys.exit(1) 