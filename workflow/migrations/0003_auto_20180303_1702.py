# Generated by Django 2.0.2 on 2018-03-03 09:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20180303_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proceeding',
            name='current_user',
            field=models.ForeignKey(null=True, on_delete='CASCADE', to=settings.AUTH_USER_MODEL),
        ),
    ]
