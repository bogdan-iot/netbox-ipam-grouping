# NetBox IPAM Grouping and Applications

A [NetBox](https://github.com/netbox-community/netbox) plugin that lets you group IPAM objects (IP Addresses, Prefixes, IP Ranges) into named **Groups** and assign them to **Applications**, with ownership-scoped editing based on NetBox's native Ownership model (introduced in NetBox 4.5).

## Features

- **Applications** — standalone entities with a name, slug, and owner. Used to represent systems or services that own IPAM resources.
- **Groups** — named collections of IP Addresses, Prefixes, and IP Ranges, linked to an Application and an Owner.
- **Ownership scoping** — non-admin users can only see and edit Groups and Applications belonging to Owners they are members of.
- **IPAM object scoping** — when editing a Group, the IP Address / Prefix / IP Range pickers are filtered to objects the user owns (via the `fra_application` custom field).
- **Native NetBox Ownership** — uses `users.Owner` (NetBox 4.5+) rather than raw Django users/groups.

## Requirements

- NetBox >= 4.5.0
- Python >= 3.10

## Installation

```bash
pip install netbox-ipam-grouping
```

Add the plugin to your NetBox `configuration.py`:

```python
PLUGINS = [
    "netbox_ipam_grouping",
]
```

Run migrations:

```bash
python netbox/manage.py migrate netbox_ipam_grouping
```

## Custom Field Setup

This plugin expects a custom field named `fra_application` of type **Object** pointing to `netbox_ipam_grouping | application`, assigned to:
- `ipam | ip address`
- `ipam | prefix`
- `ipam | ip range`

Create this in NetBox under **Customization → Custom Fields** before using the IPAM object pickers in Groups.

## Navigation

The plugin registers a **Firewall Management** top-level menu with two sections:
- **Applications** — list, add, view, edit, delete Applications
- **Groups** — list, add, view, edit, delete Groups

> **Note:** NetBox's plugin API does not currently expose a public mechanism to inject items into the built-in IPAM navigation menu. The plugin therefore registers its own top-level menu entry.

## Permissions

Grant the following NetBox object permissions to non-admin users/groups as needed:

| Model | Permissions |
|-------|-------------|
| `netbox_ipam_grouping \| application` | view, add, change, delete |
| `netbox_ipam_grouping \| group` | view, add, change, delete |

## Development

```bash
git clone https://github.com/your-org/netbox-ipam-grouping
cd netbox-ipam-grouping
pip install -e ".[dev]"
```

## Publishing to PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
