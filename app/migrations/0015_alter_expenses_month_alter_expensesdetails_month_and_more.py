# Generated by Django 5.1.2 on 2025-01-21 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_expensesdetails_year_incomesource_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='month',
            field=models.CharField(choices=[('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], max_length=50),
        ),
        migrations.AlterField(
            model_name='expensesdetails',
            name='month',
            field=models.CharField(choices=[('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], max_length=50),
        ),
        migrations.AlterField(
            model_name='incomesource',
            name='month',
            field=models.CharField(choices=[('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')], max_length=50),
        ),
    ]
