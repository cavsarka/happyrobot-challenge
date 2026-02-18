from database import engine, SessionLocal
from models import Base
from seed import seed

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Seeding database...")
    seed()

if __name__ == "__main__":
    reset_db()
    print("Database reset and seeded successfully!")