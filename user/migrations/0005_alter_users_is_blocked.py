# Generated by Django 5.1.1 on 2024-10-29 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_users_auth_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]