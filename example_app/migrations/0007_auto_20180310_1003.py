# Generated by Django 2.0.2 on 2018-03-10 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('example_app', '0006_auto_20180310_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inquiryinline',
            name='unit',
            field=models.TextField(blank=True, choices=[('L', 'L'), ('ml', 'ml'), ('mg', 'mg'), ('g', 'g'), ('ul', 'ul'), ('kg', 'kg')], default='mg', null=True, verbose_name='单位'),
        ),
    ]
