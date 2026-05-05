import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from users.models import Owner

from .models import Application, Group


class ApplicationFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(method="search", label="Search")
    owner_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Owner.objects.all(),
        label="Owner (ID)",
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        field_name="owner__name",
        queryset=Owner.objects.all(),
        to_field_name="name",
        label="Owner (name)",
    )

    class Meta:
        model = Application
        fields = ["id", "name", "slug", "owner_id", "owner"]

    def search(self, queryset, name, value):
        if value.strip():
            return queryset.filter(
                Q(name__icontains=value) |
                Q(slug__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset


class GroupFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(method="search", label="Search")
    owner_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Owner.objects.all(),
        label="Owner (ID)",
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        field_name="owner__name",
        queryset=Owner.objects.all(),
        to_field_name="name",
        label="Owner (name)",
    )
    application_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Application.objects.all(),
        label="Application (ID)",
    )
    application = django_filters.ModelMultipleChoiceFilter(
        field_name="application__name",
        queryset=Application.objects.all(),
        to_field_name="name",
        label="Application (name)",
    )

    class Meta:
        model = Group
        fields = ["id", "name", "owner_id", "owner", "application_id", "application"]

    def search(self, queryset, name, value):
        if value.strip():
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset
