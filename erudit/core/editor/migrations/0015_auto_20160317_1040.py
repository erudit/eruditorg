# -*- coding: utf-8 -*-

from django.db import migrations, models


def create_empty_files_versions(apps, schema_editor):
    IssueSubmission = apps.get_model('editor', 'IssueSubmission')
    IssueSubmissionFilesVersion = apps.get_model('editor', 'IssueSubmissionFilesVersion')
    for issue in IssueSubmission.objects.all():
        files_version = IssueSubmissionFilesVersion.objects.filter(issue_submission=issue)
        if not files_version.exists():
            issue.save_version()


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0014_auto_20160317_0945'),
    ]

    operations = [
        migrations.RunPython(create_empty_files_versions, reverse_code=migrations.RunPython.noop),
    ]
