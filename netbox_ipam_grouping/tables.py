import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import Application, Group


class ApplicationTable(NetBoxTable):
    name = tables.Column(linkify=True)
    slug = tables.Column()
    owner = tables.Column(
        linkify=lambda record: record.owner.get_absolute_url() if record.owner else None,
        verbose_name="Owner",
    )
    ipam_group_count = tables.Column(
        empty_values=(), verbose_name="Groups", orderable=False
    )
    tags = columns.TagColumn(url_name="plugins:netbox_ipam_grouping:application_list")
    actions = columns.ActionsColumn(actions=("edit", "delete"))

    class Meta(NetBoxTable.Meta):
        model = Application
        fields = (
            "pk", "name", "slug", "owner", "description",
            "ipam_group_count", "tags", "created", "last_updated", "actions",
        )
        default_columns = (
            "pk", "name", "slug", "owner", "ipam_group_count", "actions",
        )

    def render_ipam_group_count(self, record):
        return record.ipam_groups.count()


class GroupTable(NetBoxTable):
    name = tables.Column(linkify=True)
    owner = tables.Column(
        linkify=lambda record: record.owner.get_absolute_url() if record.owner else None,
        verbose_name="Owner",
    )
    application = tables.Column(
        linkify=lambda record: record.application.get_absolute_url() if record.application else None,
        verbose_name="Application",
    )
    prefix_count = tables.Column(empty_values=(), verbose_name="Prefixes", orderable=False)
    ip_count = tables.Column(empty_values=(), verbose_name="IP Addresses", orderable=False)
    range_count = tables.Column(empty_values=(), verbose_name="IP Ranges", orderable=False)
    tags = columns.TagColumn(url_name="plugins:netbox_ipam_grouping:group_list")
    actions = columns.ActionsColumn(actions=("edit", "delete"))

    class Meta(NetBoxTable.Meta):
        model = Group
        fields = (
            "pk", "name", "owner", "application", "description",
            "prefix_count", "ip_count", "range_count",
            "tags", "created", "last_updated", "actions",
        )
        default_columns = (
            "pk", "name", "owner", "application",
            "prefix_count", "ip_count", "range_count", "tags", "actions",
        )

    def render_prefix_count(self, record):
        return record.prefixes.count()

    def render_ip_count(self, record):
        return record.ip_addresses.count()

    def render_range_count(self, record):
        return record.ip_ranges.count()
