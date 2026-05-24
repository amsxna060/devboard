from pydantic import BaseModel, Field,field_validator,ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import re



    
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

    
    

