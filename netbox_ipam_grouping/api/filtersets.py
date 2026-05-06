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
    q = django_filters.CharFilter(method="search", label="Search")
    application = django_filters.CharFilter(
        method="filter_application",
        label="Application (ID)",
    )

    class Meta:
        model = Group
        fields = ["id", "name", "owner"]

    def filter_application(self, queryset, name, value):
        if not value or not value.strip():
            # Empty application param — same behaviour as IPAM fields:
            # return nothing so the picker shows empty before an app is chosen.
            return queryset.none()
        try:
            return queryset.filter(application__pk=int(value))
        except (ValueError, TypeError):
            return queryset.none()

    def filter_queryset(self, queryset):
        # If application is present in request data but empty, return none
        # immediately — mirrors ScopedIPAMFilterMixin behaviour.
        if (
            "application" in self.data
            and not self.data.get("application")
        ):
            return queryset.none()

        queryset = super().filter_queryset(queryset)
        request = getattr(self, "request", None)
        if not request or request.user.is_superuser:
            return queryset
        user = request.user
        return queryset.filter(
            Q(owner__users=user) |
            Q(owner__user_groups__in=user.groups.all())
        ).distinct()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
