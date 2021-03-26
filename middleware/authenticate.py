from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from fastapi import Header, HTTPException, status, Depends, Request
from connection.models import TokenData
from connection import load_public_key
from pydantic import BaseModel, ValidationError
from typing import List
import jwt
from jwt import InvalidTokenError
from dynaconf import settings
from loguru import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

HTTPUnauthorizedException = HTTPException(status_code=401, detail="Unauthorized")

HTTPForbiddenException = HTTPException(status_code=403, detail="Forbidden")

VINDR_LAB_API_KEY = settings.VINDR_LAB_API_KEY

class User(BaseModel):
    username: str
    roles: List[str]
    auth_info: dict
    access_token: dict


def verify_decide(r: Request):
    verify = True
    try:
        api_key_header = r.headers.get("x-api-key")
        if api_key_header == VINDR_LAB_API_KEY:
            verify = False
    except Exception as ex:
        logger.exception(ex)
    return verify


def get_authentication(authorization: str = Header(None), r: Request = Request):
    verify = verify_decide(r)

    user = User
    if authorization:
        try:
            if not authorization.startswith("Bearer"):
                raise HTTPUnauthorizedException
            bearer = authorization.split(" ")[-1]
            public_key = load_public_key()

            decoded = jwt.decode(
                bearer, key=public_key, algorithms=["RS256"], audience=settings.KC_VERIFY_AUDIENCE, verify=verify
            )
            user.username = decoded["preferred_username"]
            user.auth_info: decoded
            user.access_token = decoded
        except Exception as ex:
            logger.exception(ex)
            raise HTTPForbiddenException

    else:
        logger.error("error when get info")
        raise HTTPForbiddenException

    return user


async def verify_scopes(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), r: Request = Request
):
    verify = verify_decide(r)
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        public_key = load_public_key()

        payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=settings.KC_VERIFY_AUDIENCE,verify=verify)
        username: str = payload.get("preferred_username")
        sub: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scope").split()
        token_data = TokenData(scopes=token_scopes, username=username, sub=sub)
    except (InvalidTokenError, ValidationError):
        logger.error("error when verify_scopes")
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return token_data
