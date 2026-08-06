"""
Celery tasks for the management app.
"""

import os

from celery import shared_task
from django.utils import timezone

from management.models import Branch, Enrollment, Group, User


@shared_task
def finish_expired_groups():
    """
    Daily sweep: any 'started' group whose ends_at is yesterday or earlier
    is marked finished, and its still-enrolled students are moved off
    "enrolled" for that group — the same two updates an admin would make by
    hand once a course's schedule has run out.
    """
    today = timezone.localdate()
    expired_groups = Group.objects.filter(
        is_active=True,
        status=Group.Status.STARTED,
        ends_at__isnull=False,
        ends_at__lt=today,
    )

    finished_count = 0
    student_count = 0
    for group in expired_groups:
        group.status = Group.Status.FINISHED
        group.save(update_fields=["status", "updated_at"])

        updated = group.enrollments.filter(
            is_active=True,
            status=Enrollment.Status.ENROLLED,
        ).update(status=Enrollment.Status.FINISHED)

        finished_count += 1
        student_count += updated

    return f"Finished {finished_count} expired group(s), {student_count} student(s) moved to finished."


@shared_task
def import_excel_task(file_path, actor_id, branch_id):
    """
    Runs the legacy-data Excel import (management/import_excel.py) in the
    background — the file has thousands of rows, comfortably past what an
    HTTP request should sit open for. Removes the temporary upload from
    disk once done, success or failure, either way.
    """
    from management.import_excel import import_excel_data

    actor = User.objects.filter(pk=actor_id).first()
    branch = Branch.objects.filter(pk=branch_id).first()
    try:
        summary = import_excel_data(file_path, actor, branch)
        return summary
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass
