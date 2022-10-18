'''
view for recipe
'''

from rest_framework import viewsets,mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core import models
from recipe import serializers


class RecipeView(viewsets.ModelViewSet):
    '''
    View for manage recipe
    '''
    
    serializer_class = serializers.RecipeDetailSerializer
    queryset = models.Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        '''
        change serializer depending on the endpoint
        '''
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class
        
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)
        

class TageView(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    ''' views for tags'''
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()
    authentication_classes =[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ''' filter for current user'''
        return self.queryset.filter(user = self.request.user) 
    
class IngredientView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    ''' views for Ingredients'''
    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredients.objects.all()
    authentication_classes =[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ''' filter for current user'''
        return self.queryset.filter(user = self.request.user) 
    