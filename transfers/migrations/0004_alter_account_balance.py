# Generated by Django 5.1 on 2024-08-21 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transfers', '0003_remove_account_temp_field_alter_trasaction_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=models.FloatField(default=0.0),
        ),
    ]
