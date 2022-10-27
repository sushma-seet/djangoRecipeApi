'''
Serializers for Movie APIs
'''

from dataclasses import field
from email.errors import NonPrintableDefect
from pyexpat import model
from rest_framework import serializers

from core import models


class CharacterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Characters
        fields =['id','name']
        read_only_fields = ['id']
        
class MovieSerializer(serializers.ModelSerializer):
    
    characters = CharacterSerializer(many = True, required = False)
    
    def get_or_create(self,characters,movie):
        user = self.context['request'].user
        for character in characters:
            character_obj,create = models.Characters.objects.get_or_create(
                user = user,
                **character
            )
            movie.characters.add(character_obj)
        
    class Meta:
        model = models.Movie
        fields = ['id','name','release_date','ratings','director','producer','characters']
        read_only_fields = ['id']
        
    def create(self,validated_data):
        ''' Create character with movie'''
        characters = validated_data.pop('characters',[])
        movie = models.Movie.objects.create(**validated_data)
        self.get_or_create(characters, movie)
        return movie
    
    def update(self,instance, validated_data):
        ''' updating movie and characters'''
        
        characters = validated_data.pop('characters',[])
        if characters is not None:
            instance.characters.clear()
            self.get_or_create(characters, instance)
            
        for k,v in validated_data.items():
            setattr(instance,k,v)
        instance.save()
        
        return instance 
        
class MovieDetailSerializer(MovieSerializer):
    
    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields
        

class CharacterDetailSerializer(CharacterSerializer):
    
    class Meta(CharacterSerializer.Meta):
        fields = CharacterSerializer.Meta.fields
        read_only_fields = ['id']
    
    
        