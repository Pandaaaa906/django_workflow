# Generated by Django 2.0.2 on 2018-03-10 01:09

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.query_utils
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20180306_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flow',
            name='process_obj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='flownode',
            name='approval_group_type',
            field=models.ForeignKey(blank=True, default=None, limit_choices_to=django.db.models.query_utils.Q(('app_label', 'auth'), django.db.models.query_utils.Q(('model', 'user'), ('model', 'group'), _connector='OR'), _connector='AND'), null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='flownode',
            name='condition',
            field=jsonfield.fields.JSONField(blank=True, default={'attr': None, 'operator': None, 'type': None, 'value': None}, null=True),
        ),
        migrations.AlterField(
            model_name='flownode',
            name='flow',
            field=models.ForeignKey(db_column='flow_id', on_delete=django.db.models.deletion.PROTECT, to='workflow.Flow'),
        ),
        migrations.AlterField(
            model_name='flownode',
            name='next_node',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='backword', to='workflow.FlowNode'),
        ),
        migrations.AlterField(
            model_name='flownode',
            name='previous_node',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='forward', to='workflow.FlowNode'),
        ),
        migrations.AlterField(
            model_name='proceeding',
            name='flow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='workflow.Flow'),
        ),
        migrations.AlterField(
            model_name='proceeding',
            name='node',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='workflow.FlowNode'),
        ),
        migrations.AlterField(
            model_name='proceeding',
            name='voucher_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
    ]
