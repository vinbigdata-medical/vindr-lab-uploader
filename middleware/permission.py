from typing import List
from fastapi import HTTPException, Depends, Request, Header
from .authenticate import User, get_authentication
from loguru import logger
from dynaconf import settings


def require_perms(perms):
    def f(user: User = Depends(get_authentication)):
        return validate_permission(user, perms=perms, logic="and")

    return f


def require_at_least_one_perm(perms):
    def f(user: User = Depends(get_authentication)):
        return validate_permission(user, perms=perms, logic="or")

    return f


def validate_permission(user: User = Depends(get_authentication), perms: List[str] = [], logic="or"):
    if user is None:
        return

    ok = []
    for perm in perms:
        user_perms = user.access_token["authorization"]["permissions"]
        splitted = perm.split("#")
        required_resource = splitted[0]
        required_scopes = set(splitted[1].split(","))
        for provided_perm in user_perms:
            if provided_perm["rsname"] == required_resource:
                provided_scopes = set(provided_perm["scopes"])
                if required_scopes.issubset(provided_scopes):
                    if logic == "or":
                        return
                    ok.append(True)
                    continue
    if len(ok) == len(perms):
        return
    raise HTTPException(status_code=401, detail="Unauthorized")
