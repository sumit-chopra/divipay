from rest_framework import serializers
from .models import Card, Control

class CardSerializer(serializers.ModelSerializer):
        class Meta:
                model = Card
                fields = ('id','user', 'balance', 'created', 'updated')

class ControlSerializer(serializers.ModelSerializer):
        card_id = serializers.CharField(write_only=True)
        class Meta:
                model = Control
                fields = ("control_name", "control_value", "card_id", "id")