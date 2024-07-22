import re

from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):

    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    def get_rating(self, obj):
        return obj.get_rating()

    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        fields = 'id', 'text', 'author', 'score', 'pub_date'
        model = Review

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)

        if (
            request.method == 'POST'
            and Review.objects.filter(
                author=request.user, title=title).exists()
        ):
            raise ValidationError('Нельзя добавить 2 отзыв, только 1')
        return data

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка от 0 до 10!')
        return value


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        fields = 'id', 'text', 'author', 'pub_date', 'review', 'author'
        model = Comment


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Требуется только буквы, цифры и @/./+/-/_.'
            )
        return value


class UserRegistrationSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        pass


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        pass


class UserUpdateSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']
