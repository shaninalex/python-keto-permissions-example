from src.models import DB, User
from src.permissions import Permissions
from src.request import Request, process


def main():
    db = DB()
    perms = Permissions()
    user_a = db.get_user("jeff@theworker.com")
    user_b = db.get_user("mike@theworker.com")

    # request 1
    req = Request(db=db, path="/api/v1/orders", method="POST", headers={"X-User": user_a.id})
    resp = process(req, perms, db)
    print(f"Response from {user_a.email} request: {resp}")

    # request 2
    req = Request(db=db, path="/api/v1/orders", method="POST", headers={"X-User": user_b.id})
    resp = process(req, perms, db)
    print(f"Response from {user_b.email} request: {resp}")

    # request 3
    req = Request(db=db, path="/api/v1/orders", method="GET", headers={"X-User": user_b.id})
    resp = process(req, perms, db)
    print(f"Response from {user_b.email} request: {resp}")


if __name__ == '__main__':
    main()
