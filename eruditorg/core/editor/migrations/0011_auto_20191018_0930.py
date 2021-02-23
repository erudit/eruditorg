# Generated by Django 2.0.13 on 2019-10-18 13:30

from django.db import migrations


def migrate_needs_correction_issue_submissions(apps, schema_editor):
    IssueSubmission = apps.get_model("editor", "IssueSubmission")
    for issue in IssueSubmission.objects.all():
        last_status_track = issue.status_tracks.order_by("-created").first()
        if issue.status == "D" and last_status_track is not None:
            issue.status = "C"
            issue.save()


class Migration(migrations.Migration):

    dependencies = [
        ("editor", "0010_auto_20191017_0813"),
    ]

    operations = [migrations.RunPython(migrate_needs_correction_issue_submissions)]
