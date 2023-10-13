# Generated by Django 3.2.5 on 2022-03-16 00:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_clubs', '0005_alter_user_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='meeting_cycle',
            field=models.IntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(limit_value=0, message='Meeting cycle must not be lower than 0.')]),
        ),
    ]