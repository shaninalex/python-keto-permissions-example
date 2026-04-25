from src.models import DB
from src.permissions import Permissions


def main():
    db = DB()
    perms = Permissions()
    perms.bootstrap()

    for user in db.get_users():
        for group in user.groups:
            perms.assign_user_to_group(user.id, group)


if __name__ == '__main__':
    main()
