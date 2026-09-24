from django.db import migrations


def align_thresholds(apps, schema_editor):
    SystemSetting = apps.get_model('settings', 'SystemSetting')
    values = {
        'normal_threshold': ('0', 'Below the Arduino alert threshold (cm)'),
        'alert_threshold': ('45', 'Arduino alert boundary (cm)'),
        'warning_threshold': ('60', 'Arduino warning boundary (cm)'),
        'danger_threshold': ('75', 'Arduino danger boundary (cm)'),
    }
    for key, (value, description) in values.items():
        SystemSetting.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(align_thresholds, migrations.RunPython.noop),
    ]
