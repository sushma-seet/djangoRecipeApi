'''
testing recipe api

'''
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from core import models
from recipe import serializers


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe):
    '''return detail url for perticular recipe'''
    return reverse('recipe:recipe-detail',args=[recipe.id])
    


def create_recipe(user, **params):
    '''
    create recipe
    '''
    default = {
        'title' : 'sample title',
        'time_minutes': 5,
        'price' : Decimal('2.43'),
        'link':'https//sample-recipes.com',
        'description':'sample description',
        
    }
    
    default.update(params)
    recipe = models.Recipe.objects.create(
        user = user,
        **default
    )
    return recipe

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    '''
    Test creating recipe with public user
    
    '''
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_recipe_requires_authorization(self):
        '''
        requires authorization
        '''
        
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateRecipeAPITests(TestCase):
    
    '''
    Test API with authorized user
    '''
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email ='user@example.com',password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = models.Recipe.objects.all().order_by('-id')
        serializer = serializers.RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_retrieve_recipes_limited_to_users(self):
        '''
        Test retrieve recipes limited to user
        
        '''
        user_2 = create_user(
            email = 'user2@gmail.com',
            password = 'user1234',
        )
        
        create_recipe(user=user_2)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = serializers.RecipeSerializer(recipes, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_get_detail_recipe(self):
        '''
        testing get recipe details
        '''
        
        recipe = create_recipe(self.user)
        url = detail_url(recipe)
        
        res = self.client.get(url)
        serializer = serializers.RecipeDetailSerializer(recipe)
        
        self.assertEqual(res.data, serializer.data)
        
    def test_create_recipe(self):
        '''
        test create recipe
        '''
        payload = {
            'title':'salad',
            'time_minutes':5,
            'price':Decimal('2.5'),
        }
        
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        recipe = models.Recipe.objects.get(
            id = res.data['id']
        )
        
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
        self.assertEqual(recipe.user, self.user)
        
    def test_partial_update(self):
        '''
        test updating recipe 
        '''
        price = Decimal('4.1')
        time_taken = 6
        recipe = create_recipe(
            user = self.user,
            title ='sample title',
            time_minutes = time_taken,
            price = price,
        )
        
        payload = {'title':'new title'}
        url = detail_url(recipe)
        res = self.client.patch(url,payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.time_minutes,time_taken)
        self.assertEqual(recipe.price,price)
        
        
        
        
        