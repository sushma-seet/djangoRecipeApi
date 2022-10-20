'''
view for recipe
'''

from rest_framework import viewsets,mixins,status

from rest_framework.decorators import action
from rest_framework.response import Response
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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class
        
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)
        
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
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
        return self.queryset.filter(user = self.request.user).order_by('-name')
    