from django.db.models import Q


class OwnershipQueryParamFilterMixin:
    """
    Filters IPAM objects to those whose ipam_application custom field points
    to an Application owned by the given user (directly or via user_group).
    """

    def filter_owned_by_user(self, queryset, name, value):
        if not value:
            return queryset

        from django.contrib.auth import get_user_model
        try:
            user = get_user_model().objects.get(pk=value)
        except get_user_model().DoesNotExist:
            return queryset.none()

        from netbox_ipam_grouping.models import Application
        app_pks = list(
            Application.objects.filter(
                Q(owner__users=user) |
                Q(owner__user_groups__in=user.groups.all())
            ).distinct().values_list("pk", flat=True)
        )

        if not app_pks:
            return queryset.none()

        return queryset.filter(
            custom_field_data__ipam_application__in=app_pks
        ).distinct()
