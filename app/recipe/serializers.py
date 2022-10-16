'''
serializers for our recipe app
'''



from rest_framework import serializers
from core import models


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Serializers for recipe app
    '''
    
    class Meta:
        model = models.Recipe
        fields = ['id','title','time_minutes','price','link']
        read_only_fields = ['id']
        
class RecipeDetailSerializer(RecipeSerializer):
    '''
    Serializer for detail api
    '''
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields+['description']


