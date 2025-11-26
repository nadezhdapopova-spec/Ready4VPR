from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Создает модератора, если он не создан"

    def handle(self, *args, **options):
        user = get_user_model()
        try:
            if not user.objects.filter(email="moderator1@sky.pro").exists():
                user = user.objects.create_user(
                    email="moderator1@sky.pro",
                    password="234qwe567rty",
                    first_name="Moderator1",
                    last_name="Moderator1",
                    username="Moderator1",
                    is_staff=True,
                )

                group, _ = Group.objects.get_or_create(name="moderators")
                user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f"Модератор {user.email} успешно создан"))
            else:
                self.stdout.write(self.style.WARNING("Модератор уже существует"))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Ошибка создания Moderator1: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Неожиданная ошибка: {e}"))
