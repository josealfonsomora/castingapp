# Generated by Django 3.0.3 on 2020-02-12 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200212_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='authentication_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='validated',
            field=models.BooleanField(default=False),
        ),
    ]