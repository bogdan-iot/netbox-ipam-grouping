import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("ipam", "0001_initial"),
        ("users", "0015_owner"),
        ("extras", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="name")),
                ("slug", models.SlugField(max_length=100, unique=True, verbose_name="slug")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("owner", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="applications",
                    to="users.owner",
                    verbose_name="owner",
                )),
            ],
            options={"ordering": ("name",), "verbose_name": "application", "verbose_name_plural": "applications"},
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict)),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("owner", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="ipam_groups",
                    to="users.owner",
                    verbose_name="owner",
                )),
                ("application", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="ipam_groups",
                    to="netbox_ipam_grouping.application",
                    verbose_name="application",
                )),
                ("prefixes", models.ManyToManyField(
                    blank=True,
                    related_name="ipam_groups",
                    to="ipam.prefix",
                    verbose_name="prefixes",
                )),
                ("ip_addresses", models.ManyToManyField(
                    blank=True,
                    related_name="ipam_groups",
                    to="ipam.ipaddress",
                    verbose_name="IP addresses",
                )),
                ("ip_ranges", models.ManyToManyField(
                    blank=True,
                    related_name="ipam_groups",
                    to="ipam.iprange",
                    verbose_name="IP ranges",
                )),
            ],
            options={"ordering": ("name",), "verbose_name": "group", "verbose_name_plural": "groups"},
        ),
        migrations.AddField(
            model_name="application",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="+", to="extras.tag"),
        ),
        migrations.AddField(
            model_name="group",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="+", to="extras.tag"),
        ),
    ]
