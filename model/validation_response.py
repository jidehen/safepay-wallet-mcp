from pydantic import BaseModel

class ValidationResponse(BaseModel):
    sufficient_credit: bool
    daily_limit_ok: bool
    card_active: bool 