# Generated by Django 3.2.5 on 2022-03-29 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book_clubs', '0014_message'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set(),
        ),
    ]