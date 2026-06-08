from django.db.models import Q
from netbox.api.viewsets import NetBoxModelViewSet
from users.models import ObjectPermission

from ..utils import has_unrestricted_permission
from ..models import Application, Group
from .serializers import ApplicationSerializer, GroupSerializer
from .filtersets import ApplicationAPIFilterSet, GroupAPIFilterSet


# ------------------------------------------------------------------
# Shared helper (mirrors the one in the UI views)
# ------------------------------------------------------------------

def _ownership_filter(qs, user):
    """Filter a queryset to objects owned by the given user."""
    return qs.filter(
        Q(owner__users=user) |
        Q(owner__user_groups__in=user.groups.all())
    ).distinct()


# ------------------------------------------------------------------
# Viewsets
# ------------------------------------------------------------------

ACTION_MAP = {
    'list':    'view',
    'retrieve': 'view',
    'create':  'add',
    'update':  'change',
    'partial_update': 'change',
    'destroy': 'delete',
}


class ApplicationViewSet(NetBoxModelViewSet):
    queryset = Application.objects.prefetch_related("owner", "tags")
    serializer_class = ApplicationSerializer
    filterset_class = ApplicationAPIFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return qs

        action = ACTION_MAP.get(self.action, 'view')
        if has_unrestricted_permission(self.request, action, 'netbox_ipam_grouping', 'application'):
            return qs

        return _ownership_filter(qs, user)


class GroupViewSet(NetBoxModelViewSet):
    queryset = Group.objects.prefetch_related(
        "owner", "application", "member_groups",
        "prefixes", "ip_addresses", "ip_ranges", "tags",
    )
    serializer_class = GroupSerializer
    filterset_class = GroupAPIFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return qs

        action = ACTION_MAP.get(self.action, 'view')
        if has_unrestricted_permission(self.request, action, 'netbox_ipam_grouping', 'group'):
            return qs

        return _ownership_filter(qs, user)
