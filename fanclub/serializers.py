from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    sender = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField(required=False)