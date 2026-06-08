from netbox.api.serializers import NetBoxModelSerializer
from users.api.serializers import OwnerSerializer
from rest_framework import serializers

from ipam.api.serializers import PrefixSerializer, IPAddressSerializer, IPRangeSerializer
from ipam.models import Prefix, IPAddress, IPRange

from ..models import Application, Group


class ApplicationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_ipam_grouping-api:application-detail"
    )

    owner = OwnerSerializer(nested=True, required=False, allow_null=True)

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

    application = ApplicationSerializer(nested=True)

    # Writable as PKs — field names match the model M2M fields exactly,
    # so DRF's ModelSerializer.create() handles .set() automatically.
    prefixes = serializers.PrimaryKeyRelatedField(
        queryset=Prefix.objects.all(), many=True, required=False
    )
    ip_addresses = serializers.PrimaryKeyRelatedField(
        queryset=IPAddress.objects.all(), many=True, required=False
    )
    ip_ranges = serializers.PrimaryKeyRelatedField(
        queryset=IPRange.objects.all(), many=True, required=False
    )

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

    def to_representation(self, instance):
        # On reads, return full nested objects instead of bare PKs
        ret = super().to_representation(instance)
        ret['prefixes'] = PrefixSerializer(
            instance.prefixes.all(), many=True, nested=True, context=self.context
        ).data
        ret['ip_addresses'] = IPAddressSerializer(
            instance.ip_addresses.all(), many=True, nested=True, context=self.context
        ).data
        ret['ip_ranges'] = IPRangeSerializer(
            instance.ip_ranges.all(), many=True, nested=True, context=self.context
        ).data
        return ret
