# Generated by Django 5.1.2 on 2024-10-19 22:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_expenses_expensestype_expensesdetails_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenses',
            name='date',
            field=models.DateField(default='2024-10-20'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expenses',
            name='month',
            field=models.CharField(choices=[('janurary', 'January'), ('february', 'February'), ('marth', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], default=datetime.datetime(2024, 10, 19, 22, 12, 41, 35239, tzinfo=datetime.timezone.utc), max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expenses',
            name='pending_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='spent_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='status',
            field=models.CharField(choices=[('pending', 'pendong'), ('done', 'done')], default='pending', max_length=30),
        ),
        migrations.AlterField(
            model_name='incomesource',
            name='month',
            field=models.CharField(choices=[('janurary', 'January'), ('february', 'February'), ('marth', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], max_length=50),
        ),
    ]
