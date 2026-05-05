import django_filters
from ipam.filtersets import PrefixFilterSet, IPAddressFilterSet, IPRangeFilterSet
from .ipam_filters import OwnershipQueryParamFilterMixin


class ScopedIPAMFilterMixin(OwnershipQueryParamFilterMixin):
    """
    Added to the core IPAM filtersets to support two query params:

    owned_by_user=<pk>
        Restricts results to objects whose fra_application custom field
        points to an Application owned by that user.

    cf_fra_application= (present but empty)
        Happens when the Group form's $application reference resolves to ""
        because no application has been selected yet. Return nothing so the
        pickers show empty before an application is chosen.
    """

    owned_by_user = django_filters.NumberFilter(method="filter_owned_by_user")

    def filter_queryset(self, queryset):
        # If cf_fra_application is explicitly in the request but has no value,
        # $application resolved to "" → no application selected → return empty.
        if (
            "cf_fra_application" in self.data
            and not self.data.get("cf_fra_application")
        ):
            return queryset.none()
        return super().filter_queryset(queryset)


class ScopedPrefixFilterSet(ScopedIPAMFilterMixin, PrefixFilterSet):
    pass


class ScopedIPAddressFilterSet(ScopedIPAMFilterMixin, IPAddressFilterSet):
    pass


class ScopedIPRangeFilterSet(ScopedIPAMFilterMixin, IPRangeFilterSet):
    pass
