from rest_framework import serializers

class MangaDownloadSerializer(serializers.Serializer):
    manga_name = serializers.CharField()
    chapters = serializers.ListField(child=serializers.IntegerField())
