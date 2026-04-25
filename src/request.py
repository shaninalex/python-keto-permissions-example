from dataclasses import dataclass
from typing import Any

from src.models import DB
from src.permissions import Permissions

# path prefix → keto namespace (must match config/namespaces.keto.ts)
OBJECTS_PATHS = {
    "Order": ["/api/v1/orders"],
}

METHODS_ACTIONS = {
    "POST": "create",
    "PATCH": "patch",
    "DELETE": "delete",
    "GET": "read",
}

@dataclass(frozen=True)
class Request:
    path: str
    method: str
    headers: dict
    db: DB



@dataclass(frozen=True)
class Response:
    data: Any
    status: int = 200


def process(request: Request, perms: Permissions, db: DB) -> Response:
    namespace = _resolve_object(request.path)
    if namespace is None:
        return Response(status=404, data="not found")

    action = METHODS_ACTIONS.get(request.method)
    if action is None:
        return Response(status=405, data=f"method {request.method} not allowed")

    user_id = request.headers.get("X-User")
    if not user_id:
        return Response(status=401, data="missing X-User header")

    if not perms.check(user_id, namespace, action):
        return Response(
            status=403,
            data=f"forbidden: user {user_id} cannot {action} {namespace}",
        )

    if namespace == "Order" and action == "read":
        return Response(data=db.get_orders())

    return Response(data=f"process request for {namespace} with action {action}", status=200)


def _resolve_object(path: str) -> str | None:
    for name, paths in OBJECTS_PATHS.items():
        if any(path == p or path.startswith(p + "/") for p in paths):
            return name
    return None
