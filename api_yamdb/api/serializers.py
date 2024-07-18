from django.forms import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title, Review, Comment


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        slug_field='slug',
        read_only=True, many=True)
    category = SlugRelatedField(
        slug_field='slug',
        read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')


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
