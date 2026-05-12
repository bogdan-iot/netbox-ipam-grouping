import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_ipam_grouping', '0002_alter_application_custom_field_data_and_more'),
    ]

    operations = [
        # Remove the single parent FK
        migrations.RemoveField(
            model_name='group',
            name='parent',
        ),
        # Add the self-referential M2M for group membership
        migrations.AddField(
            model_name='group',
            name='member_groups',
            field=models.ManyToManyField(
                blank=True,
                related_name='parent_groups',
                to='netbox_ipam_grouping.group',
                verbose_name='member groups',
            ),
        ),
    ]
