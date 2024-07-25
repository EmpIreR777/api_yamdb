from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment
from .validators import validate_username

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = {
            'name': instance.category.name,
            'slug': instance.category.slug,
        }
        data['genre'] = [
            {
                'name': genre.name,
                'slug': genre.slug,
            } for genre in instance.genre.all()
        ]
        if self.context['request'].stream.method == 'PATCH':
            data['rating'] = instance.rating
        else:
            data['rating'] = None
        return data


class TitleSerializer(serializers.ModelSerializer):

    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    rating = serializers.FloatField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
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


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True, max_length=150, validators=[validate_username]
    )

    class Meta:
        model = User
        fields = ['email', 'username']

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        user_with_email = User.objects.filter(email=email).first()
        user_with_username = User.objects.filter(username=username).first()

        if user_with_email and user_with_username:
            if user_with_email != user_with_username:
                raise serializers.ValidationError(
                    'Email и Username принадлежат разным пользователям.'
                )
        elif user_with_email:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        elif user_with_username:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )
        return data


class ConfirmRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        pass


class UserUpdateSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']
