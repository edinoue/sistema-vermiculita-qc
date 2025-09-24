# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0005_make_analysis_type_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='display_order',
            field=models.PositiveIntegerField(default=0, help_text='Ordem em que o produto aparece nas listas', verbose_name='Ordem de Exibição'),
        ),
        migrations.AddField(
            model_name='property',
            name='display_order',
            field=models.PositiveIntegerField(default=0, help_text='Ordem em que a propriedade aparece nos formulários', verbose_name='Ordem de Exibição'),
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['display_order', 'name'], 'verbose_name': 'Produto', 'verbose_name_plural': 'Produtos'},
        ),
        migrations.AlterModelOptions(
            name='property',
            options={'ordering': ['display_order', 'category', 'name'], 'verbose_name': 'Propriedade', 'verbose_name_plural': 'Propriedades'},
        ),
    ]
