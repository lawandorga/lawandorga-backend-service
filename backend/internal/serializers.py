from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from backend.internal.models import Article, InternalUser


class ArticleSerializer(ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'description', 'date', 'id']


class ArticleDetailSerializer(ModelSerializer):
    author = serializers.SerializerMethodField('get_author')

    class Meta:
        model = Article
        fields = '__all__'

    def get_author(self, obj):
        if obj.author:
            return obj.author.user.name
        return None
