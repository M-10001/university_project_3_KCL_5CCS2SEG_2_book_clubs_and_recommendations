# Generated by Django 3.2.5 on 2022-04-05 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_clubs', '0015_alter_book_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='book',
            name='name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='book',
            name='publisher',
            field=models.CharField(max_length=1000),
        ),
    ]