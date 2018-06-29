# Generated by Django 2.0.2 on 2018-06-29 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('example_app', '0003_auto_20180629_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inquiryinline',
            name='parent_voucher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiryinline', to='example_app.Inquiry', verbose_name='单据'),
        ),
        migrations.AlterField(
            model_name='inquiryinline',
            name='unit',
            field=models.TextField(blank=True, choices=[('kg', 'kg'), ('L', 'L'), ('ul', 'ul'), ('ml', 'ml'), ('mg', 'mg'), ('g', 'g')], default='mg', null=True, verbose_name='单位'),
        ),
    ]
