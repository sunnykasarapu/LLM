from enum import Enum

from fastapi import Header, HTTPException, status


class Role(str, Enum):
    admin = "admin"
    evaluator = "evaluator"
    viewer = "viewer"


ROLE_RANK = {Role.viewer: 1, Role.evaluator: 2, Role.admin: 3}


def require_role(minimum: Role):
    def dependency(x_role: str = Header(default=Role.admin.value), x_actor_id: str = Header(default="system")) -> dict:
        try:
            role = Role(x_role)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role") from exc
        if ROLE_RANK[role] < ROLE_RANK[minimum]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return {"actor_id": x_actor_id, "role": role.value}

    return dependency

