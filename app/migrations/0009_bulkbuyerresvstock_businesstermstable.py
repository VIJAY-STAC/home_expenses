# Generated by Django 5.1.2 on 2024-11-20 19:39

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_expensesdetails_income_sorce'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkBuyerResvStock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, max_length=100)),
                ('last_synced_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BusinessTermsTable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('term_name', models.CharField(db_index=True, max_length=30, unique=True)),
                ('term_value', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
