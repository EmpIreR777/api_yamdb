from django.contrib import admin

from reviews.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name',

    )
    search_fields = ('username', 'role',)
    list_filter = ('username',)