'''
Tets for ingredients api

'''

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredients
from recipe.serializers import IngredientSerializer



INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email = 'test_user@gmail.com',password= 'test123'):
    '''creating user for testing'''
    return get_user_model().objects.create(email=email, password=password)

class PublicIngredientApiTests(TestCase):
    ''' Testing Ingredients with public user'''
        
    def setUp(self):
        ''' Test client'''
        self.client = APIClient()
        
    def test_retrieve_ingredients_with_unauthorized_user(self):
        '''Testing trieving ingredients with unauthenticated user '''
        
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateIngredientApiTests(TestCase):
    ''' Testing Ingredients api with authorized user'''
    
    def setUp(self) :
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        
        
    def test_retrieve_ingredients_with_authorized_user(self):
        ''' Testing retrieving ingredients'''
        
        Ingredients.objects.create(user = self.user, name ='Chilli Powder')
        Ingredients.objects.create(user = self.user, name ='Sugar')
        
        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_Ok)
        self.assertEqual(res.data, serializer.data)
        
        
    def test_retrieve_limited_to_user(self):
        ''' Testing retrieving ingredients limited to authorized user'''
        
        user2 = create_user(email='test2@gmail.com', password='test12345')
        Ingredients.objects.create(
            user = user2,
            name = 'Vanilla'
        )
        
        ingredient = Ingredients.objects.create(user = self.user, name = 'Browine')
        
        res = self.client.get(INGREDIENTS_URL)
        
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)
        self.assertEqual(res.data[0]['id'],ingredient.id)
    
        
        