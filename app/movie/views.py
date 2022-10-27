'''
Views for Movie APIs
'''

from movie import serializers
from rest_framework import viewsets 
from core import models

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated



class MovieView(viewsets.ModelViewSet):
    
    ''' View set for Movie'''
    
    serializer_class = serializers.MovieDetailSerializer
    queryset = models.Movie.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        ''' filter with authorized user'''
        return self.queryset.filter(user = self.request.user).order_by('-id')
    
    def perform_create(self, serializer):
        ''' save serializer'''
        serializer.save(user = self.request.user)
        
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MovieSerializer
        
        return self.serializer_class
    
class CharacterView(viewsets.ModelViewSet):
    
    ''' View set for Character'''
    
    serializer_class = serializers.CharacterDetailSerializer
    queryset = models.Characters.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        ''' filter with authorized user'''
        return self.queryset.filter(user = self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        ''' save serializer'''
        serializer.save(user = self.request.user)
        
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CharacterSerializer
        
        return self.serializer_class
        
    
        
    
    
    