from pydantic import BaseModel, Field,field_validator,ConfigDict
from typing import Optional, List
from datetime import datetime

# UserCreate — for registration input
#    fields: email (str), name (str, min 2 chars), password (str, min 6 chars)
#    validator: email must contain @ and . stored lowercase
#    validator: name strip whitespace

class UserCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True
    )
    email:str
    name : str = Field(...,min_length=2)
    password : str = Field(...,min_length=6)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        email = value.strip().lower()
        if not '@' in value or not '.' in value:
            raise ValueError('Invalid Email')
        return email
    
    # I created this because you asked but I know it is unncessary if I create Config
    @field_validator('name')
    @classmethod
    def validate_name(cls,value):
        return value.strip()
    
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
    is_active:bool
    created_at:datetime

# 3. MessageOut — generic response
#    fields: message (str)

class MessageOut(BaseModel):
    message:str

    

    

