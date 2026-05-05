from netbox.plugins import PluginConfig


class NetboxIpamGroupingConfig(PluginConfig):
    name = "netbox_ipam_grouping"
    verbose_name = "IPAM Grouping and Applications"
    description = (
        "Group IP addresses, prefixes, and IP ranges into named groups "
        "and assign them to applications, with ownership-scoped editing."
    )
    version = "1.0.0"
    author = "Your Organisation"
    author_email = "netbox@example.com"
    base_url = "ipam-grouping"
    min_version = "4.5.0"
    required_settings = []
    default_settings = {}
    menu = "navigation.menu"

    def ready(self):
        super().ready()
        from ipam.api.views import PrefixViewSet, IPAddressViewSet, IPRangeViewSet
        from .api.extensions import (
            ScopedPrefixFilterSet,
            ScopedIPAddressFilterSet,
            ScopedIPRangeFilterSet,
        )
        PrefixViewSet.filterset_class = ScopedPrefixFilterSet
        IPAddressViewSet.filterset_class = ScopedIPAddressFilterSet
        IPRangeViewSet.filterset_class = ScopedIPRangeFilterSet


config = NetboxIpamGroupingConfig
