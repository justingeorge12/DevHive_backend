# Generated by Django 5.1.1 on 2024-10-24 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_users_is_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='skill',
            field=models.CharField(blank=True),
        ),
    ]