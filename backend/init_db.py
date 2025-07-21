from database import SessionLocal, engine, init_db
from models import Base, FamilyOffice, Employee
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_demo_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(FamilyOffice).first()
        if existing:
            logger.info("Demo data already exists, skipping...")
            return
        
        # Create two family offices
        smith_office = FamilyOffice(name="Smith Family Office")
        jones_office = FamilyOffice(name="Jones Family Office")
        
        db.add(smith_office)
        db.add(jones_office)
        db.commit()
        
        # Add employees for Smith Family Office
        smith_employees = [
            Employee(family_office_id=smith_office.id, name="John Butler", salary=75000),
            Employee(family_office_id=smith_office.id, name="Mary Chef", salary=65000),
            Employee(family_office_id=smith_office.id, name="Robert Driver", salary=55000),
            Employee(family_office_id=smith_office.id, name="Sarah Nanny", salary=50000),
            Employee(family_office_id=smith_office.id, name="James Gardener", salary=45000),
        ]
        
        # Add employees for Jones Family Office
        jones_employees = [
            Employee(family_office_id=jones_office.id, name="Emily Assistant", salary=60000),
            Employee(family_office_id=jones_office.id, name="Michael Security", salary=70000),
            Employee(family_office_id=jones_office.id, name="Lisa Housekeeper", salary=48000),
        ]
        
        db.add_all(smith_employees + jones_employees)
        db.commit()
        
        logger.info("Demo data created successfully!")
        logger.info(f"Created {len(smith_employees)} employees for Smith Family Office")
        logger.info(f"Created {len(jones_employees)} employees for Jones Family Office")
        
    except Exception as e:
        logger.error(f"Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Seeding demo data...")
    seed_demo_data()