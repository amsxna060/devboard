from pydantic import BaseModel, Field,field_validator,ConfigDict,model_validator
from typing import Optional, List
from datetime import datetime, timezone
import re
from model import TaskStatus



    
# 2. UserOut — for API response (never expose password)
#    fields: id, email, name, role, is_active, created_at
#    model_config: from_attributes=True

class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id:int
    email:str
    name:str
    role:Optional[str] = "user"
    is_active:Optional[bool] = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# 3. MessageOut — generic response
#    fields: message (str)

class MessageOut(BaseModel):
    message:str

# 4. 
class UserRegister(BaseModel):
    model_config = ConfigDict(from_attributes=True,str_strip_whitespace=True)
    email: str
    name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=6)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        email = value.strip().lower()
        if not '@' in email or not '.' in email:
            raise ValueError('Invalid Email')
        return email
    
    @field_validator('password')
    @classmethod
    def validate_strong_password(cls, value:str):
        pattern = r'^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*\d).{6,}$'
        if not bool(re.match(pattern,value)):
            raise ValueError('Please Write Strong Password')
        return value
        
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ProjectCreate — name (required, min 2), description (optional)
class ProjectCreate(BaseModel):
    name : str = Field(...,min_length=2)
    description : Optional[str] = None

# ProjectOut — id, name, description, owner_id, created_at, from_attributes=True
class ProjectOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id:int
    name:str = Field(...,min_length=2)
    description:Optional[str] = None
    owner_id : int
    created_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ProjectUpdate — name optional, description optional (for PATCH)
class ProjectUpdate(BaseModel):
    name:Optional[str] = Field(None,min_length=2)
    description:Optional[str] = None


# TaskCreate — title (required), description (optional), status (optional, default todo)
#              priority (1-5), due_date (optional), project_id, assignee_id (optional)
class TaskCreate(BaseModel):
    title:str
    description:Optional[str]
    status:Optional[TaskStatus] = TaskStatus.TODO
    priority:int = Field(default=1,ge=1,le=5)
    due_date:Optional[datetime]
    project_id:int
    assignee_id:Optional[int]

    @model_validator(mode="after")
    def validate_due_date(self):
        if self.due_date:
            if self.due_date < datetime.now(timezone.utc):
                raise ValueError("Due Date Must be Future")
        return self

    
# TaskOut — all fields + from_attributes=True
class TaskOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id:int
    title:str
    description:Optional[str]
    status:Optional[TaskStatus] = TaskStatus.TODO
    priority:int= Field(default=1,ge=1,le=5)
    due_date:Optional[datetime]
    project_id:int
    assignee_id:Optional[int]
    
# TaskUpdate — all fields optional (for PATCH)
class TaskUpdate(BaseModel):
    title:Optional[str] = None
    description:Optional[str] = None
    status:Optional[TaskStatus] = None
    priority:Optional[int] = Field(None,ge=1,le=5) 
    due_date:Optional[datetime] = None
    project_id:Optional[int] = None
    assignee_id:Optional[int] = None

class BulkAssignRequest(BaseModel):
    task_ids : List[int]
    assignee_id : int
    

    
    

