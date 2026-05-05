import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from ..models import Application, Group


class ApplicationAPIFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(method="search", label="Search")

    class Meta:
        model = Application
        fields = ["id", "name", "slug", "owner"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value)
        )


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