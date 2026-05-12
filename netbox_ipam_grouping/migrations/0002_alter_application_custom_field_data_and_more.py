import django.db.models.deletion
import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_ipam_grouping', '0001_initial'),
        ('extras', '0001_initial'),
    ]

    operations = [
        # Update Django's internal migration state to match how NetBoxModel
        # actually defines custom_field_data and tags — without touching the
        # database. The tags field is M2M and cannot be altered via ALTER TABLE;
        # SeparateDatabaseAndState lets us sync the state only.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='application',
                    name='custom_field_data',
                    field=models.JSONField(blank=True, default=dict),
                ),
                migrations.AlterField(
                    model_name='application',
                    name='tags',
                    field=models.ManyToManyField(
                        blank=True, related_name='+', to='extras.tag'
                    ),
                ),
                migrations.AlterField(
                    model_name='group',
                    name='custom_field_data',
                    field=models.JSONField(blank=True, default=dict),
                ),
                migrations.AlterField(
                    model_name='group',
                    name='tags',
                    field=models.ManyToManyField(
                        blank=True, related_name='+', to='extras.tag'
                    ),
                ),
            ],
            database_operations=[],  # No actual DB changes needed
        ),

        # Add the parent FK for nested groups
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='children',
                to='netbox_ipam_grouping.group',
                verbose_name='parent group',
            ),
        ),
    ]
