"""
Celery tasks for the management app.
"""

from celery import shared_task
from django.utils import timezone

from management.models import Enrollment, Group


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
