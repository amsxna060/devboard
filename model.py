from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String, Boolean, DateTime
from datetime import datetime, timezone
from database import Base

class User(Base):
    __table__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True) # integer, Primary key
    email:Mapped[str] = mapped_column(String(255),unique=True,nullable=False)     # string(255), unique, not nullable
    name :Mapped[str] =  mapped_column(String(100),nullable=False)     #→ string(100), not nullable
    password_hash : Mapped[str] = mapped_column(String(255),nullable=False) #→ string(255), not nullable
    role :Mapped[str]  = mapped_column(String(50),default="user")  #   → string(50), default "user"
    is_active :Mapped[bool] = mapped_column(Boolean,default=True)  #→ boolean, default True
    # Why use lambda here, and timezone = True?
    created_at :Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc)) #→ DateTime, default = now (utc)
