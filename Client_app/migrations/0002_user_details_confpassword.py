# Generated by Django 5.2.2 on 2025-06-10 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_details',
            name='confpassword',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
