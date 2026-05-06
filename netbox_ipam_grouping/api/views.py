from django.db.models import Q
from netbox.api.viewsets import NetBoxModelViewSet

from ..models import Application, Group
from .serializers import ApplicationSerializer, GroupSerializer
from .filtersets import ApplicationAPIFilterSet, GroupAPIFilterSet


class ApplicationViewSet(NetBoxModelViewSet):
    queryset = Application.objects.prefetch_related("owner", "tags")
    serializer_class = ApplicationSerializer
    filterset_class = ApplicationAPIFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(
            Q(owner__users=user) |
            Q(owner__user_groups__in=user.groups.all())
        ).distinct()


class GroupViewSet(NetBoxModelViewSet):
    queryset = Group.objects.prefetch_related(
        "owner", "application", "member_groups", "prefixes", "ip_addresses", "ip_ranges", "tags",
    )
    serializer_class = GroupSerializer
    filterset_class = GroupAPIFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(
            Q(owner__users=user) |
            Q(owner__user_groups__in=user.groups.all())
        ).distinct()
