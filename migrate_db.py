import os
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)

def migrate_database():
    """Add new columns to the features table for storing commit_id, patch_file_path, and analysis_file_path"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logging.error("DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            logging.info("Checking existing columns...")
            
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'features'
            """))
            
            existing_columns = [row[0] for row in result]
            logging.info(f"Existing columns: {existing_columns}")
            
            if 'commit_id' not in existing_columns:
                logging.info("Adding commit_id column...")
                conn.execute(text("ALTER TABLE features ADD COLUMN commit_id VARCHAR(100)"))
                conn.commit()
                logging.info("✓ commit_id column added")
            else:
                logging.info("commit_id column already exists")
            
            if 'patch_file_path' not in existing_columns:
                logging.info("Adding patch_file_path column...")
                conn.execute(text("ALTER TABLE features ADD COLUMN patch_file_path VARCHAR(500)"))
                conn.commit()
                logging.info("✓ patch_file_path column added")
            else:
                logging.info("patch_file_path column already exists")
            
            if 'analysis_file_path' not in existing_columns:
                logging.info("Adding analysis_file_path column...")
                conn.execute(text("ALTER TABLE features ADD COLUMN analysis_file_path VARCHAR(500)"))
                conn.commit()
                logging.info("✓ analysis_file_path column added")
            else:
                logging.info("analysis_file_path column already exists")
            
            logging.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    migrate_database()
