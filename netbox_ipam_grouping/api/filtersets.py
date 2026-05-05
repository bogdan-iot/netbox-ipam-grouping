from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models import Application, Group


class GroupAPIFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = Group
        fields = ["id", "name", "owner", "application"]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        request = getattr(self, "request", None)
        if not request or request.user.is_superuser:
            return queryset
        user = request.user
        return queryset.filter(
            Q(owner__users=user) |
            Q(owner__user_groups__in=user.groups.all())
        ).distinct()
