'''
Serializers for Movie APIs
'''

from dataclasses import field
from pyexpat import model
from rest_framework import serializers

from core import models



class MovieSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Movie
        fields = ['id','name','release_date','ratings','director','producer']
        read_only_fields = ['id']
        
class MovieDetailSerializer(MovieSerializer):
    
    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields
        
class CharacterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Characters
        fields =['id','name']
        read_only_fields = ['id']
        