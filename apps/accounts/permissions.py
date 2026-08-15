from enum import Enum

from apps.accounts.models import Role


class Permission(str, Enum):
    ACCESS_PRIVATE_AREA = "access_private_area"
    MANAGE_CONTENT = "manage_content"
    MANAGE_PRAYER_REQUESTS = "manage_prayer_requests"
    MANAGE_FINANCES = "manage_finances"
    MANAGE_EVENT_OPERATIONS = "manage_event_operations"
    MANAGE_MINISTRY_SCHEDULES = "manage_ministry_schedules"
    MANAGE_USERS = "manage_users"
    MANAGE_TWO_FACTOR = "manage_two_factor"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    Role.MEMBER: {
        Permission.ACCESS_PRIVATE_AREA,
    },
    Role.MINISTRY_LEADER: {
        Permission.ACCESS_PRIVATE_AREA,
        Permission.MANAGE_MINISTRY_SCHEDULES,
    },
    Role.COMMUNICATION: {
        Permission.ACCESS_PRIVATE_AREA,
        Permission.MANAGE_CONTENT,
        Permission.MANAGE_PRAYER_REQUESTS,
    },
    Role.PASTOR: {
        Permission.ACCESS_PRIVATE_AREA,
        Permission.MANAGE_CONTENT,
        Permission.MANAGE_PRAYER_REQUESTS,
    },
    Role.TREASURY: {
        Permission.ACCESS_PRIVATE_AREA,
        Permission.MANAGE_FINANCES,
    },
    Role.EVENTS_COMMISSION: {
        Permission.ACCESS_PRIVATE_AREA,
        Permission.MANAGE_EVENT_OPERATIONS,
    },
    Role.ADMIN: set(Permission),
}


def get_user_role(user) -> str | None:
    if not user or not getattr(user, "is_authenticated", False):
        return None
    profile = getattr(user, "profile", None)
    if profile is None:
        return None
    return profile.role


def user_has_permission(user, permission: Permission) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    role = get_user_role(user)
    if role is None:
        return False
    return permission in ROLE_PERMISSIONS.get(role, set())
