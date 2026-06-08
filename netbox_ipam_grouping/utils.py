from django.db.models import Q
from users.models import ObjectPermission


def has_unrestricted_permission(request, action, app_label, model):
    """
    Returns True if the user has an unconstrained ObjectPermission
    for the given action and model, either directly or via a group.
    """
    return ObjectPermission.objects.filter(
        actions__contains=[action],
        constraints__isnull=True,
    ).filter(
        object_types__app_label=app_label,
        object_types__model=model,
    ).filter(
        Q(users=request.user) |
        Q(groups__in=request.user.groups.all())
    ).exists()
