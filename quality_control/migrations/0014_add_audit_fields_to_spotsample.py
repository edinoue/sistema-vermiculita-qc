# Generated manually to add audit fields to SpotSample

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0013_fix_spot_sample_field'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='spotsample',
            name='created_by',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.PROTECT, 
                related_name='spotsample_created', 
                to=settings.AUTH_USER_MODEL, 
                verbose_name='Criado por'
            ),
        ),
        migrations.AddField(
            model_name='spotsample',
            name='updated_by',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.PROTECT, 
                related_name='spotsample_updated', 
                to=settings.AUTH_USER_MODEL, 
                verbose_name='Atualizado por'
            ),
        ),
    ]
