# Generated manually to fix SpotSample inheritance

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0013_fix_spot_sample_field'),
    ]

    operations = [
        # Esta migração não precisa fazer nada no banco
        # pois apenas mudamos a herança do modelo
        # Os campos created_at e updated_at já existem
    ]
