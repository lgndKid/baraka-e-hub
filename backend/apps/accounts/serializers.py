from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nom", "email", "role", "date_inscription")
        read_only_fields = ("id", "email", "role", "date_inscription")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "nom", "email", "password", "consentement_donnees")
        read_only_fields = ("id",)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte existe deja avec cet email.")
        return value

    def validate_consentement_donnees(self, value):
        if not value:
            raise serializers.ValidationError(
                "Le consentement au traitement des donnees est obligatoire."
            )
        return value

    def validate(self, attrs):
        validate_password(attrs["password"], User(email=attrs["email"], nom=attrs["nom"]))
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        try:
            pk = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=pk, is_active=True)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Lien invalide ou expire.")
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Lien invalide ou expire.")
        validate_password(attrs["new_password"], user)
        attrs["user"] = user
        return attrs


class RoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices)


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()
