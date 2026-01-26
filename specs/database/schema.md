# Database Schema Specification

## 🗄️ Database Overview
- **Database**: Neon PostgreSQL
- **ORM**: SQLModel for Python
- **Models**: User and Task entities
- **Relationships**: One-to-many (User → Tasks)

## 📊 SQLModel Models

### User Model
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    """User model for authentication and task ownership"""
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    email: str = Field(
        unique=True,
        index=True,
        min_length=5,
        max_length=100
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationship to tasks
    tasks: list["Task"] = Relationship(back_populates="user")
```

### Task Model
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class Task(SQLModel, table=True):
    """Task model for todo items"""
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True
    )
    title: str = Field(
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    completed: bool = Field(
        default=False
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="tasks")
```

## 🔗 Database Schema (SQL)

### Tables
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_users_email (email)
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_completed (completed)
);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 🔄 Database Operations

### User Operations
```python
# Create user
user = User(email="user@example.com")
session.add(user)
session.commit()

# Get user with tasks
user = session.get(User, user_id)
tasks = user.tasks

# Filter users
users = session.exec(select(User).where(User.email.like("%@example.com"))).all()
```

### Task Operations
```python
# Create task for user
task = Task(
    user_id=user_id,
    title="Buy groceries",
    description="Milk, bread, eggs",
    completed=False
)
session.add(task)
session.commit()

# Get user's tasks
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()

# Update task
task = session.get(Task, task_id)
if task and task.user_id == user_id:  # Security check
    task.title = "Updated title"
    task.completed = True
    session.add(task)
    session.commit()

# Delete task
task = session.get(Task, task_id)
if task and task.user_id == user_id:  # Security check
    session.delete(task)
    session.commit()
```

## 🛡️ Security & Isolation

### User Isolation
- **Foreign Key**: All tasks have user_id foreign key
- **Cascading Delete**: Tasks deleted when user deleted
- **Query Filtering**: All queries must filter by user_id
- **Authorization**: Backend validates user_id matches JWT

### Indexes for Performance
- **Users**: Email index for authentication
- **Tasks**: User_id index for filtering
- **Tasks**: Completed index for status queries

### Data Validation
- **Email Format**: Validated at application level
- **Title Length**: 1-200 characters enforced
- **Description Length**: Max 1000 characters
- **Boolean Values**: Explicit true/false for completed

## 🔄 Migration Strategy

### Initial Migration
```python
from sqlmodel import create_engine, SQLModel

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Create tables
SQLModel.metadata.create_all(engine)
```

### Future Migrations
- Use Alembic for schema migrations
- Version-controlled migration files
- Automated migration scripts
- Rollback capabilities

## 📈 Performance Considerations

### Query Optimization
- **Index Usage**: All foreign keys indexed
- **Pagination**: Implement for large task lists
- **Caching**: Consider Redis for frequently accessed data
- **Connection Pooling**: Configure pool size for production

### Scaling Considerations
- **Read Replicas**: For read-heavy workloads
- **Sharding**: For very large user bases
- **Caching**: Redis for session and query caching
- **Monitoring**: Query performance tracking