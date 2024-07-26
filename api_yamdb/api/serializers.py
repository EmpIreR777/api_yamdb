from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Title, Review
from reviews.validators import validate_username

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
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        fields = 'id', 'text', 'author', 'pub_date', 'author'
        model = Comment


class BaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True, max_length=150, validators=[validate_username]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        user_with_email = User.objects.filter(email=email).exists()
        user_with_username = User.objects.filter(username=username).exists()
        user_email_first = User.objects.filter(email=email).first()
        user_username_first = User.objects.filter(username=username).first()

        errors = {}
        if user_email_first and user_username_first:
            if user_email_first != user_username_first:
                errors['email'] = 'Email принадлежит другому пользователю.'
                errors['username'] = 'Username принадлежит другому пол-лю.'
                raise serializers.ValidationError(errors)

        elif user_with_email and not user_with_username:
            errors['email'] = 'Пользователь с таким email существует.'
            raise serializers.ValidationError(errors)

        elif not user_with_email and user_with_username:
            errors['username'] = 'Пользователь с таким username существует.'
            raise serializers.ValidationError(errors)

        return data


class UserRegistrationSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ('email', 'username')


class ConfirmRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неправильный код подтверждения')

        data['user'] = user
        return data


class UserSerializer(BaseUserSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
