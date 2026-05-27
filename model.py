from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String, Boolean, DateTime,ForeignKey,Enum as SAEnum
from datetime import datetime, timezone
from database import Base
from typing import Optional, List
import enum

class TimestampMixin:
    __slots__ = ()
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  default=lambda:datetime.now(timezone.utc),
                                                  onupdate=lambda:datetime.now(timezone.utc))
    
class SoftDeleteMixin:
    __slots__ = ()
    deleted_at : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True),default=None,nullable=True)

    @property
    def is_deleted(self)-> bool:
        if self.deleted_at is None:
            return False
        return True

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True) # integer, Primary key
    email:Mapped[str] = mapped_column(String(255),unique=True,nullable=False)     # string(255), unique, not nullable
    name :Mapped[str] =  mapped_column(String(100),nullable=False)     #→ string(100), not nullable
    password_hash : Mapped[str] = mapped_column(String(255),nullable=False) #→ string(255), not nullable
    role :Mapped[str]  = mapped_column(String(50),default="user")  #   → string(50), default "user"
    is_active :Mapped[bool] = mapped_column(Boolean,default=True)  #→ boolean, default True
    # Why use lambda here, and timezone = True?
    created_at :Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc)) #→ DateTime, default = now (utc)

    projects:Mapped[List["Project"]] = relationship(back_populates="owner")
    assigned_tasks: Mapped[List["Task"]] = relationship(back_populates="assignee")


# Project has:
# id, name, description, owner_id (FK → users.id), created_at
class Project(TimestampMixin,SoftDeleteMixin, Base):
    __tablename__ = "projects"
    id:Mapped[int] = mapped_column(primary_key=True)
    name :Mapped[str] =  mapped_column(String(100),nullable=False) 
    description:Mapped[Optional[str]] = mapped_column(String(1000),nullable=True)
    owner_id : Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)

    owner:Mapped["User"] = relationship(back_populates="projects")
    tasks: Mapped[List["Task"]] = relationship(back_populates="project")

# Task model needs:
# id, title, description (optional), status (TaskStatus enum, default TODO)
# priority (int, default 1)
# due_date (datetime, optional)
# project_id (FK → projects.id)
# assignee_id (FK → users.id, optional — task may be unassigned)
# created_at

# Relationships:
# project → Project
# assignee → User (optional)

# Project model needs tasks relationship added:
# tasks: Mapped[List["Task"]] = relationship(back_populates="project")

# User model needs assigned_tasks relationship:
# assigned_tasks: Mapped[List["Task"]] = relationship(back_populates="assignee")


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(TimestampMixin,SoftDeleteMixin, Base):
    __tablename__ = "tasks"
    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(200),nullable=False)
    description:Mapped[Optional[str]] = mapped_column(String(1000),nullable=True)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus),default=TaskStatus.TODO)
    priority: Mapped[int] = mapped_column(default=1)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True),nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"),nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"),nullable=True)
  
    assignee : Mapped[Optional["User"]] = relationship(back_populates="assigned_tasks")
    project: Mapped["Project"] = relationship(back_populates="tasks")