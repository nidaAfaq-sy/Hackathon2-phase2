from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from typing import Generator
from settings import settings
import logging
import os
# Import models to register them with SQLModel
from models import User, Task

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Use NullPool for serverless environments (Vercel)
is_serverless = os.environ.get("VERCEL", False)

# Create database engine for Neon PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,  # Better for serverless
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30,
    } if "neon.tech" in settings.DATABASE_URL else {}
)


def create_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session


def migrate_user_table():
    """Add missing columns to user table if they don't exist, fix existing columns"""
    try:
        with engine.begin() as conn:
            # Check if created_at column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name = 'created_at'
                AND table_schema = current_schema()
            """))
            row = result.fetchone()
            print(f"[MIGRATION] Column check result: {row}")
            if not row:
                # Add created_at column
                print("[MIGRATION] Column created_at not found, adding it...")
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                """))
                print("[MIGRATION] Successfully added created_at column!")
            else:
                print("[MIGRATION] Column created_at already exists")
            
            # Check if hashed_password column exists and if it's nullable
            result2 = conn.execute(text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name = 'hashed_password'
                AND table_schema = current_schema()
            """))
            hashed_pwd_row = result2.fetchone()
            if hashed_pwd_row and hashed_pwd_row[0] == 'NO':
                # Make hashed_password nullable since we're using email-only auth
                print("[MIGRATION] Making hashed_password column nullable...")
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ALTER COLUMN hashed_password DROP NOT NULL
                """))
                print("[MIGRATION] Successfully made hashed_password nullable!")
            
            # Check if id column is integer (should be UUID)
            result3 = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name = 'id'
                AND table_schema = current_schema()
            """))
            id_type_row = result3.fetchone()
            if id_type_row and id_type_row[0] in ('integer', 'bigint', 'serial'):
                # Change id column from integer to UUID
                # First check if table has data
                count_result = conn.execute(text('SELECT COUNT(*) FROM "user"'))
                row_count = count_result.scalar()
                print(f"[MIGRATION] Found {row_count} existing rows")
                
                # First, drop the default value (it's incompatible with UUID)
                print("[MIGRATION] Dropping default value from id column...")
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN id DROP DEFAULT'))
                
                # Check if task table exists and has foreign key
                fk_check = conn.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE constraint_name = 'task_user_id_fkey'
                """))
                fk_exists = fk_check.fetchone()
                
                if fk_exists:
                    print("[MIGRATION] Dropping foreign key constraint from task table...")
                    conn.execute(text('ALTER TABLE "task" DROP CONSTRAINT IF EXISTS task_user_id_fkey'))
                
                if row_count > 0:
                    # If there's data, we need to handle UUID generation differently
                    # Since we can't use gen_random_uuid() directly in USING for multiple rows,
                    # we'll create a new UUID column, populate it, then swap
                    print("[MIGRATION] WARN Table has existing data. Migrating to UUID...")
                    # Add temporary UUID column
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN id_new UUID'))
                    # Generate UUIDs for existing rows
                    conn.execute(text("""
                        UPDATE "user" 
                        SET id_new = gen_random_uuid()
                    """))
                    
                    # Drop old id column (CASCADE will handle dependent objects)
                    print("[MIGRATION] Dropping old id column...")
                    conn.execute(text('ALTER TABLE "user" DROP COLUMN id CASCADE'))
                    # Rename new column to id
                    conn.execute(text('ALTER TABLE "user" RENAME COLUMN id_new TO id'))
                    # Make it primary key again
                    conn.execute(text('ALTER TABLE "user" ADD PRIMARY KEY (id)'))
                else:
                    # No data, safe to change type directly
                    print("[MIGRATION] Table is empty, changing id column type to UUID...")
                    # Just change the type - no USING needed for empty table
                    conn.execute(text("""
                        ALTER TABLE "user" 
                        ALTER COLUMN id TYPE UUID
                    """))
                print("[MIGRATION] Successfully changed id column to UUID!")
            elif id_type_row:
                print(f"[MIGRATION] id column is already {id_type_row[0]} type")
    except Exception as e:
        # Log the error for debugging
        print(f"[MIGRATION] Exception: {e}")
        import traceback
        traceback.print_exc()
        # If table doesn't exist yet, that's fine - create_tables will handle it
        if "does not exist" not in str(e) and "relation" not in str(e).lower():
            raise


def migrate_task_table():
    """Migrate task table: add embedding column, convert id and user_id to UUID"""
    try:
        with engine.begin() as conn:
            # Check if task table exists
            table_check = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'task' 
                AND table_schema = current_schema()
            """))
            if not table_check.fetchone():
                print("[MIGRATION] Task table does not exist yet, skipping migration")
                return
            
            # 1. Add embedding column if it doesn't exist
            embedding_check = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'task' 
                AND column_name = 'embedding'
                AND table_schema = current_schema()
            """))
            if not embedding_check.fetchone():
                print("[MIGRATION] Adding 'embedding' column to task table...")
                conn.execute(text("""
                    ALTER TABLE "task" 
                    ADD COLUMN embedding TEXT DEFAULT '[]'
                """))
                print("[MIGRATION] Successfully added 'embedding' column!")
            else:
                print("[MIGRATION] 'embedding' column already exists")
            
            # 2. Convert id column from integer to UUID if needed
            id_type_check = conn.execute(text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'task'
                AND column_name = 'id'
                AND table_schema = current_schema()
            """))
            id_type_row = id_type_check.fetchone()
            
            if id_type_row and id_type_row[0] in ('integer', 'bigint', 'serial'):
                print(f"[MIGRATION] task.id column is {id_type_row[0]}, converting to UUID...")
                count_result = conn.execute(text('SELECT COUNT(*) FROM "task"'))
                row_count = count_result.scalar()
                print(f"[MIGRATION] Found {row_count} existing rows in task table")
                
                # Drop default if it exists (PostgreSQL doesn't support IF EXISTS here)
                # So we check first, then drop
                default_check = conn.execute(text("""
                    SELECT column_default
                    FROM information_schema.columns
                    WHERE table_name = 'task'
                    AND column_name = 'id'
                    AND table_schema = current_schema()
                """))
                default_row = default_check.fetchone()
                if default_row and default_row[0]:
                    print("[MIGRATION] Dropping default value from id column...")
                    conn.execute(text('ALTER TABLE "task" ALTER COLUMN id DROP DEFAULT'))
                
                if row_count > 0:
                    # Has data: create new UUID column, populate, swap
                    print("[MIGRATION] Table has data, migrating with new column...")
                    conn.execute(text('ALTER TABLE "task" ADD COLUMN id_new UUID'))
                    conn.execute(text('UPDATE "task" SET id_new = gen_random_uuid()'))
                    conn.execute(text('ALTER TABLE "task" DROP COLUMN id CASCADE'))
                    conn.execute(text('ALTER TABLE "task" RENAME COLUMN id_new TO id'))
                    conn.execute(text('ALTER TABLE "task" ADD PRIMARY KEY (id)'))
                    # Add default UUID generation
                    conn.execute(text('ALTER TABLE "task" ALTER COLUMN id SET DEFAULT gen_random_uuid()'))
                else:
                    # Empty table: drop and recreate column as UUID
                    print("[MIGRATION] Table is empty, dropping and recreating id column as UUID...")
                    conn.execute(text('ALTER TABLE "task" DROP COLUMN id CASCADE'))
                    conn.execute(text('ALTER TABLE "task" ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid()'))
                
                print("[MIGRATION] Successfully converted task.id to UUID!")
            elif id_type_row:
                print(f"[MIGRATION] task.id column is already {id_type_row[0]} type")
            
            # 3. Convert user_id column from integer to UUID if needed
            user_id_type_check = conn.execute(text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'task'
                AND column_name = 'user_id'
                AND table_schema = current_schema()
            """))
            user_id_type_row = user_id_type_check.fetchone()
            
            if user_id_type_row and user_id_type_row[0] in ('integer', 'bigint'):
                print(f"[MIGRATION] task.user_id column is {user_id_type_row[0]}, converting to UUID...")
                count_result = conn.execute(text('SELECT COUNT(*) FROM "task"'))
                row_count = count_result.scalar()
                
                # Drop foreign key constraint first if it exists
                fk_check = conn.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE constraint_name = 'task_user_id_fkey'
                """))
                if fk_check.fetchone():
                    print("[MIGRATION] Dropping foreign key constraint...")
                    conn.execute(text('ALTER TABLE "task" DROP CONSTRAINT IF EXISTS task_user_id_fkey'))
                
                if row_count > 0:
                    # Has data: drop and recreate column (can't map integer to UUID)
                    print("[MIGRATION] WARN Task table has data. Dropping and recreating user_id as UUID...")
                    print("[MIGRATION] WARN Note: Existing task.user_id values will be cleared.")
                    conn.execute(text('ALTER TABLE "task" DROP COLUMN user_id CASCADE'))
                    conn.execute(text('ALTER TABLE "task" ADD COLUMN user_id UUID'))
                else:
                    # Empty table: drop and recreate (safer than USING cast)
                    print("[MIGRATION] Table is empty, recreating user_id column as UUID...")
                    conn.execute(text('ALTER TABLE "task" DROP COLUMN user_id CASCADE'))
                    conn.execute(text('ALTER TABLE "task" ADD COLUMN user_id UUID'))
                
                # Recreate foreign key constraint if user table exists
                user_table_check = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'user' 
                    AND table_schema = current_schema()
                """))
                if user_table_check.fetchone():
                    print("[MIGRATION] Recreating foreign key constraint...")
                    conn.execute(text("""
                        ALTER TABLE "task" 
                        ADD CONSTRAINT task_user_id_fkey 
                        FOREIGN KEY (user_id) 
                        REFERENCES "user"(id)
                    """))
                print("[MIGRATION] Successfully converted task.user_id to UUID!")
            elif user_id_type_row:
                print(f"[MIGRATION] task.user_id column is already {user_id_type_row[0]} type")
                
    except Exception as e:
        print(f"[MIGRATION] Exception in migrate_task_table: {e}")
        import traceback
        traceback.print_exc()
        if "does not exist" not in str(e) and "relation" not in str(e).lower():
            raise


def test_db_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"[DB] OK Database connection successful: {version[:50]}...")
            return True
    except Exception as e:
        print(f"[DB] FAIL Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_user_table_structure():
    """Check the current structure of the user table"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'user'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            print(f"[DB] User table columns: {[col[0] for col in columns]}")
            return columns
    except Exception as e:
        print(f"[DB] FAIL Failed to check table structure: {e}")
        return None


def init_db():
    """Initialize database"""
    print("[DB] Testing database connection...")
    if not test_db_connection():
        print("[DB] WARN Database connection test failed, but continuing...")
    
    print("[DB] Checking user table structure...")
    check_user_table_structure()
    
    print("[DB] Creating tables...")
    create_tables()
    
    print("[DB] Running migrations...")
    migrate_user_table()
    migrate_task_table()
    
    print("[DB] Final table structure:")
    check_user_table_structure()