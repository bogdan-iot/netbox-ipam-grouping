from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ipam.api.serializers import PrefixSerializer, IPAddressSerializer, IPRangeSerializer

from ..models import Application, Group


class ApplicationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_ipam_grouping-api:application-detail"
    )

    class Meta:
        model = Application
        fields = (
            "id", "url", "display", "name", "slug", "description",
            "owner", "tags", "custom_fields", "created", "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "slug")


class GroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_ipam_grouping-api:group-detail"
    )

    prefixes = PrefixSerializer(nested=True, many=True, read_only=True)
    ip_addresses = IPAddressSerializer(nested=True, many=True, read_only=True)
    ip_ranges = IPRangeSerializer(nested=True, many=True, read_only=True)

    ip_addresses_count = serializers.IntegerField(read_only=True)
    prefixes_count = serializers.IntegerField(read_only=True)
    ip_ranges_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = (
            "id", "url", "display", "name", "description",
            "owner", "application",
            "member_groups",
            "prefixes", "ip_addresses", "ip_ranges",
            "ip_addresses_count", "prefixes_count", "ip_ranges_count",
            "tags", "custom_fields", "created", "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "description")
