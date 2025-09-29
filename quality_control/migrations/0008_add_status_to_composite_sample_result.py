# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0007_create_import_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='compositesampleresult',
            name='status',
            field=models.CharField(
                choices=[
                    ('APPROVED', 'Aprovado'),
                    ('ALERT', 'Alerta'),
                    ('REJECTED', 'Reprovado')
                ],
                default='APPROVED',
                max_length=20,
                verbose_name='Status'
            ),
        ),
    ]





