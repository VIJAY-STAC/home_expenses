# Generated by Django 5.1.1 on 2024-12-15 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_expensestype_discription'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenses',
            name='year',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
