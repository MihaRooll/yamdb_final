# Generated by Django 3.2 on 2023-01-10 01:31

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(validators=[reviews.validators.true_years_validator]),
        ),
        migrations.DeleteModel(
            name='TitleGenre',
        ),
    ]