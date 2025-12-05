from django.apps import AppConfig


class LmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lms"

    def ready(self):
        from django_celery_beat.models import IntervalSchedule, PeriodicTask
        import json

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=24,
            period=IntervalSchedule.HOURS,
        )

        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name="Block nonactive users",
            task="lms.tasks.block_nonactive_user",
            args=json.dumps([]),
        )
