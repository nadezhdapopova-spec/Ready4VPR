from django.contrib import admin

from lms.models import Course, Lesson


@admin.register(Course)
class CoursesAdmin(admin.ModelAdmin):
    """Добавляет курсы в админ-панель"""

    list_display = ("id", "title", "preview", "description", "price")
    list_editable = ("title", "preview", "description", "price")
    search_fields = (
        "id",
        "title",
    )


@admin.register(Lesson)
class LessonsAdmin(admin.ModelAdmin):
    """Добавляет уроки в админ-панель"""

    list_display = ("id", "title", "category", "owner", "price", "created_at")
    list_editable = ("title", "category", "owner", "price")
    list_filter = ("category", "owner")
    search_fields = ("id", "title")
