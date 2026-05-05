from ipam.filtersets import PrefixFilterSet, IPAddressFilterSet, IPRangeFilterSet
from .ipam_filters import OwnershipQueryParamFilterMixin


class OwnershipScopedFilterMixin(OwnershipQueryParamFilterMixin):
    pass


class ScopedPrefixFilterSet(OwnershipQueryParamFilterMixin, PrefixFilterSet):
    pass


class ScopedIPAddressFilterSet(OwnershipQueryParamFilterMixin, IPAddressFilterSet):
    pass


class ScopedIPRangeFilterSet(OwnershipQueryParamFilterMixin, IPRangeFilterSet):
    pass
