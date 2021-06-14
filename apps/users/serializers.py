from rest_framework import serializers
from .models import User
import jwt
from django.conf import settings

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password'
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'created_at',
            'updated_at'
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.check_password(password):
            raise serializers.ValidationError('invalid password')

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        token = jwt.encode({"id": user.id}, settings.SECRET_KEY, algorithm="HS256")
        # redis , db 저장

        return {
            'email': user.email,
            'token': token
        }