# Generated by Django 2.0.2 on 2018-03-06 07:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('example_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InquiryInline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='新增时间')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('cat_no', models.TextField(blank=True, default=None, null=True, verbose_name='货号')),
                ('cas', models.TextField(blank=True, default=None, null=True, verbose_name='cas')),
                ('name', models.TextField(blank=True, default=None, null=True, verbose_name='名称')),
                ('quantity_unit', models.FloatField(blank=True, default=None, null=True, verbose_name='单位数量')),
                ('unit', models.TextField(blank=True, choices=[('ul', 'ul'), ('mg', 'mg'), ('L', 'L'), ('g', 'g'), ('ml', 'ml'), ('kg', 'kg')], default='mg', null=True, verbose_name='单位')),
                ('quantity', models.PositiveIntegerField(blank=True, default=1, verbose_name='数量')),
                ('created_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_app_inquiryinline_created', to=settings.AUTH_USER_MODEL, verbose_name='新建人')),
                ('modified_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_app_inquiryinline_modified', to=settings.AUTH_USER_MODEL, verbose_name='修改人')),
            ],
            options={
                'verbose_name': '询单内联',
            },
        ),
        migrations.AlterModelOptions(
            name='inquiry',
            options={'permissions': (('v_can_view_own', 'Can View Own 询单'), ('v_can_view_all', 'Can View All 询单'), ('v_can_submit_own', 'Can Submit Own 询单'), ('v_can_submit_all', 'Can Submit All 询单'), ('v_can_retract_own', 'Can Retract Own 询单'), ('v_can_retract_all', 'Can Retract All 询单'), ('p_can_handover_all', 'Can Handover All 询单'), ('p_can_approve_all', 'Can_Approve All_询单')), 'verbose_name': '询单'},
        ),
        migrations.AlterModelOptions(
            name='myvoucher',
            options={'permissions': (('v_can_view_own', 'Can View Own 测试单据'), ('v_can_view_all', 'Can View All 测试单据'), ('v_can_submit_own', 'Can Submit Own 测试单据'), ('v_can_submit_all', 'Can Submit All 测试单据'), ('v_can_retract_own', 'Can Retract Own 测试单据'), ('v_can_retract_all', 'Can Retract All 测试单据'), ('p_can_handover_all', 'Can Handover All 测试单据'), ('p_can_approve_all', 'Can_Approve All_测试单据')), 'verbose_name': '测试单据'},
        ),
        migrations.RemoveField(
            model_name='inquiry',
            name='cas',
        ),
        migrations.RemoveField(
            model_name='inquiry',
            name='cat_no',
        ),
        migrations.RemoveField(
            model_name='inquiry',
            name='name',
        ),
        migrations.RemoveField(
            model_name='inquiry',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='inquiry',
            name='quantity_unit',
        ),
        migrations.RemoveField(
            model_name='inquiry',
            name='unit',
        ),
        migrations.AddField(
            model_name='inquiry',
            name='customer',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='客户'),
        ),
        migrations.AddField(
            model_name='inquiry',
            name='sales',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='销售'),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_app_inquiry_created', to=settings.AUTH_USER_MODEL, verbose_name='新建人'),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='modified_by',
            field=models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_app_inquiry_modified', to=settings.AUTH_USER_MODEL, verbose_name='修改人'),
        ),
        migrations.AlterField(
            model_name='myvoucher',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_app_myvoucher_created', to=settings.AUTH_USER_MODEL, verbose_name='新建人'),
        ),
        migrations.AlterField(
            model_name='myvoucher',
            name='modified_by',
            field=models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_app_myvoucher_modified', to=settings.AUTH_USER_MODEL, verbose_name='修改人'),
        ),
        migrations.AddField(
            model_name='inquiryinline',
            name='parent_voucher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inlines', to='example_app.Inquiry', verbose_name='单据'),
        ),
    ]