from backend.database.database import engine
from backend.database.base import Base

# Import every model so SQLAlchemy registers them
import backend.models  # noqa: F401


def create_database():
    Base.metadata.create_all(bind=engine)
    print("=" * 60)
    print("XtremePlay database initialized successfully")
    print("=" * 60)


if __name__ == "__main__":
    create_database()