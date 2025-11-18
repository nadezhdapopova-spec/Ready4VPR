from django.core.management import call_command
from django.core.management.base import BaseCommand

from lms.models import Course, Lesson
from users.models import City, CustomUser, Payment


class Command(BaseCommand):
    help = "Add test users, courses, lessons, payments to the database from fixtures"

    def handle(self, *args, **kwargs):
        City.objects.all().delete()
        CustomUser.objects.all().delete()
        Lesson.objects.all().delete()
        Course.objects.all().delete()
        Payment.objects.all().delete()

        call_command("loaddata", "users/fixtures/cities_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены города из фикструры"))

        call_command("loaddata", "users/fixtures/users_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены пользователи из фикструры"))

        call_command("loaddata", "lms/fixtures/courses_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены курсы из фикструры"))

        call_command("loaddata", "lms/fixtures/lessons_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены уроки из фикструры"))

        call_command("loaddata", "users/fixtures/payments_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены платежи из фикструры"))

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
