# Generated by Django 3.2.19 on 2023-07-24 18:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('models', '9746_related_resource_post_save_bug'),
    ]

    add_branch_excel_exporter = """
        INSERT INTO etl_modules (
            etlmoduleid,
            name,
            description,
            etl_type,
            component,
            componentname,
            modulename,
            classname,
            config,
            icon,
            slug,
            helpsortorder,
            helptemplate)
        VALUES (
            '357d11c8-ca38-40ec-926f-1946ccfceb92',
            'Branch Excel Exporter',
            'Export a Branch Excel file from Arches',
            'export',
            'views/components/etl_modules/branch-excel-exporter',
            'branch-excel-exporter',
            'branch_excel_exporter.py',
            'BranchExcelExporter',
            '{"bgColor": "#f5c60a", "circleColor": "#f9dd6c"}',
            'fa fa-upload',
            'branch-excel-exporter',
            6,
            'branch-excel-exporter-help');
        """
    remove_branch_excel_exporter = """
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = '357d11c8-ca38-40ec-926f-1946ccfceb92');
        DELETE FROM load_event WHERE etl_module_id = '357d11c8-ca38-40ec-926f-1946ccfceb92';
        DELETE FROM etl_modules WHERE etlmoduleid = '357d11c8-ca38-40ec-926f-1946ccfceb92';
        """

    operations = [
        migrations.AlterModelOptions(
            name='maplayer',
            options={'default_permissions': (), 'managed': True, 'ordering': ('sortorder', 'name'), 'permissions': (('no_access_to_maplayer', 'No Access'), ('read_maplayer', 'Read'), ('write_maplayer', 'Create/Update'), ('delete_maplayer', 'Delete'))},
        ),
        migrations.AddField(
            model_name='tempfile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tempfile',
            name='source',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RunSQL(
            add_branch_excel_exporter,
            remove_branch_excel_exporter,
        ),
    ]