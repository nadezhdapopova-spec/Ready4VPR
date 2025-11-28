from django.contrib import admin
from lms.models import Course, Lesson


@admin.register(Course)
class CoursesAdmin(admin.ModelAdmin):
    """Добавляет курсы в админ-панель"""
    list_display = ("id", "title", "preview", "description")
    list_editable = ("title", "preview", "description")
    search_fields = ("id", "title",)


@admin.register(Lesson)
class LessonsAdmin(admin.ModelAdmin):
    """Добавляет уроки в админ-панель"""
    list_display = ("id", "title", "category", "owner", "created_at")
    list_editable = ("title", "category", "owner")
    list_filter = ("category", "owner")
    search_fields = ("id", "title")
