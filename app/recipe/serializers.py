'''
serializers for our recipe app
'''

from rest_framework import serializers
from core import models




class IngredientSerializer(serializers.ModelSerializer):
    ''' serializers for Ingredients'''
    
    class Meta:
        model = models.Ingredients
        fields = ['id','name']
        read_only_fields = ['id']
        
class TagSerializer(serializers.ModelSerializer):
    ''' serializers for tag '''
    
    class Meta:
        model = models.Tag
        fields = ['id','name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    '''
    Serializers for recipe app
    '''
    tags = TagSerializer(many =True, required = False)
    ingredients = IngredientSerializer(many =True, required = False)
    class Meta:
        model = models.Recipe
        fields = [
            'id','title','time_minutes','price','link','tags',
            'ingredients'
                  ]
        read_only_fields = ['id']
        
    def _get_or_create_tags(self,tags,recipe):
        ''' create or get the tags'''
        requested_user = self.context['request'].user
        
        for tag in tags:
            tag_obj,created = models.Tag.objects.get_or_create(
                user = requested_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
            
    def _get_or_create_ingredients(self,ingredients,recipe):
        ''' create or get the ingredients'''
        requested_user = self.context['request'].user
        
        for ingredients in ingredients:
            ingredient_obj,created = models.Ingredients.objects.get_or_create(
                user = requested_user,
                **ingredients,
            )
            recipe.ingredients.add(ingredient_obj)
        
        
    def create(self,validated_data):
        ''' creating recipe with tags'''
        tags = validated_data.pop('tags',[])
        ingredients = validated_data.pop('ingredients',[])
        recipe = models.Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags,recipe)
        self._get_or_create_ingredients(ingredients,recipe)
        
        return recipe
    
    def update(self,instance, validated_data):
        ''' updating the tags'''
        tags = validated_data.pop('tags',None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
            
        for attrs, value in validated_data.items():
            setattr(instance,attrs,value)
            
        instance.save()
        return instance
            
        
class RecipeDetailSerializer(RecipeSerializer):
    '''
    Serializer for detail api
    '''
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields+['description']
        

        


