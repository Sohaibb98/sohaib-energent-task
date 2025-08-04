"""
Database migration script for MySQL integration
"""

from database import engine, Base, Session, Message

def run_migrations():
    """Run database migrations"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_tables():
    """Drop all tables (for development only)"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
    else:
        run_migrations() 