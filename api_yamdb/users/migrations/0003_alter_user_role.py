# Generated by Django 3.2 on 2023-01-10 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('USER', 'user'), ('MODERATOR', 'moderator'), ('ADMIN', 'admin')], default='US', max_length=200),
        ),
    ]
