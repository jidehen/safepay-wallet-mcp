from pydantic import BaseModel

class ValidationRequest(BaseModel):
    user_id: str
    card_id: str
    amount: float 