from pydantic import BaseModel

class ResetPasswordRequest(BaseModel):
    phone_number: str