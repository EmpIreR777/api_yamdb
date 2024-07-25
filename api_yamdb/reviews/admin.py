from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as UAdmin

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


admin.site.site_header = "Сайт отзывов, на разные произведения"
admin.site.site_title = "Отзывы на произведения"
admin.site.index_title = "Главная страница Администратора"


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
        'short_description',
    )

    @admin.display(description='Описание')
    def short_description(self, obj):
        if len(obj.description) < 100:
            return obj.description
        else:
            return obj.description[:100] + '...'

    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = 'Введите поле'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'score',
    )
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'short_text',
        'author',
        'pub_date',
    )
    search_fields = ('review',)
    list_filter = ('review',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        if len(obj.text) < 100:
            return obj.text
        else:
            return obj.text[:100] + '...'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(User)
class UserAdmin(UAdmin):
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
