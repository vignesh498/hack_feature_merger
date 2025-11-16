"""
Database migration script to add ReleaseVersion table and update Feature table
Run this script once to migrate existing database
"""

from app import app, db, ReleaseVersion, Feature
import logging

logging.basicConfig(level=logging.INFO)

def migrate():
    with app.app_context():
        try:
            logging.info("Starting database migration for Release Version feature...")
            
            logging.info("Creating tables (release_versions if not exists)...")
            db.create_all()
            
            logging.info("Checking if release_version_id column exists in features table...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('features')]
            
            if 'release_version_id' not in columns:
                logging.info("Adding release_version_id column to features table...")
                db.session.execute(db.text(
                    "ALTER TABLE features ADD COLUMN release_version_id INTEGER REFERENCES release_versions(id)"
                ))
                db.session.commit()
                logging.info("Column added successfully!")
            else:
                logging.info("Column release_version_id already exists, skipping...")
            
            logging.info("Migration completed successfully!")
            
        except Exception as e:
            logging.error(f"Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate()
