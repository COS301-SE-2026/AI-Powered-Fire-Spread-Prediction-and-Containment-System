from pydantic import BaseModel 

class EditPasswordRequest(BaseModel):
    current_password: str 
    new_password: str 
    