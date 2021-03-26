from typing import List, Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    username: Optional[str] = None
    sub: Optional[str] = None
    scopes: List[str] = []
