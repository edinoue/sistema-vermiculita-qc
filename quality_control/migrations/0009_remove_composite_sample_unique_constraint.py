# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0008_add_status_to_composite_sample_result'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='compositesample',
            unique_together=set(),
        ),
    ]

