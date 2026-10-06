from rest_framework import serializers

from .models import MessageContact


class MessageContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageContact
        fields = ("id", "nom", "email", "message", "date")
        read_only_fields = ("id", "date")


class MessageContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageContact
        fields = ("id", "nom", "email", "message", "date", "traite")
        read_only_fields = ("id", "nom", "email", "message", "date")
