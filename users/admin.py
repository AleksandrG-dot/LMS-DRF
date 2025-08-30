from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "city", "avatar")
    list_filter = ("id", "email")
    search_fields = ("email",)
