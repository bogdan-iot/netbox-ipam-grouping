from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="Firewall Management",
    groups=(
        (
            "Applications",
            (
                PluginMenuItem(
                    link="plugins:netbox_ipam_grouping:application_list",
                    link_text="Applications",
                    permissions=["netbox_ipam_grouping.view_application"],
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_ipam_grouping:application_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["netbox_ipam_grouping.add_application"],
                        ),
                    ),
                ),
            ),
        ),
        (
            "Groups",
            (
                PluginMenuItem(
                    link="plugins:netbox_ipam_grouping:group_list",
                    link_text="Groups",
                    permissions=["netbox_ipam_grouping.view_group"],
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_ipam_grouping:group_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["netbox_ipam_grouping.add_group"],
                        ),
                    ),
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-fire",
)
