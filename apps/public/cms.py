from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import GroupPagePermission, Page

from apps.accounts.permissions import Permission as AppPermission
from apps.accounts.permissions import user_has_permission

CMS_EDITORS_GROUP_NAME = "Editores de conteúdo"
PAGE_PERMISSION_CODENAMES = ("add_page", "change_page", "publish_page")
NEWS_INDEX_SLUG = "noticias"
INSTITUTIONAL_PAGE_SEEDS = (
    ("historia", "Nossa história", "Como a igreja nasceu em Santa Leopoldina."),
    ("crencas", "Crenças", "O que cremos e confessamos."),
    ("ministerios", "Ministérios", "Como servir e participar na igreja."),
    ("lideranca", "Liderança", "Pastores e liderança da igreja."),
)


def ensure_cms_editors_group() -> Group:
    group, _ = Group.objects.get_or_create(name=CMS_EDITORS_GROUP_NAME)

    access_admin = Permission.objects.get(
        content_type__app_label="wagtailadmin",
        codename="access_admin",
    )
    group.permissions.add(access_admin)

    page_ct = ContentType.objects.get(app_label="wagtailcore", model="page")
    root = Page.get_first_root_node()
    for codename in PAGE_PERMISSION_CODENAMES:
        permission = Permission.objects.get(content_type=page_ct, codename=codename)
        GroupPagePermission.objects.get_or_create(
            group=group,
            page=root,
            permission=permission,
        )
    return group


def sync_cms_access_for_user(user) -> None:
    if not user or not getattr(user, "pk", None):
        return

    group = ensure_cms_editors_group()
    can_manage = user_has_permission(user, AppPermission.MANAGE_CONTENT)

    if can_manage:
        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        user.groups.add(group)
        return

    user.groups.remove(group)
    if user.is_superuser:
        return
    if user.is_staff and not user.groups.exists():
        user.is_staff = False
        user.save(update_fields=["is_staff"])
