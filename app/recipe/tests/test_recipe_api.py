'''
testing recipe api

'''

from email.mime import image
import tempfile
import os

from PIL import Image

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
    
def image_url(recipe_id):
    '''Generating image url for recipe'''
    return reverse('recipe:recipe-upload-image',args =[recipe_id])

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
        self.client.force_authenticate(user =self.user)

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
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
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
        
    def test_create_recipe_with_new_tags(self):
        
        '''Testing create recipe along with new tags'''
        
        payload = {
            "title":"sizzling browine",
            "time_minutes":10,
            "price":Decimal("4.0"),
            "tags":[{"name":"Dessert"},{"name":"Ice Cream"},{"name":"Sweet"}],
        }
        res = self.client.post(RECIPES_URL,payload,format ='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes =models.Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(),1)
        recipe =recipes[0]
        self.assertEqual(recipe.tags.count(),3)
        for tag in payload['tags']:
            exits = recipe.tags.filter(
                name=tag['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exits)
            
    def test_create_recipe_with_existing_tags(self):
        
        '''Testing create recipe along with existing tags'''
        
        see_food_tag = models.Tag.objects.create(name ='See Food',user =self.user)
        
        payload = {
            'title':'Fish Fingers',
            'time_minutes':60,
            'price':Decimal('5.0'),
            'tags':[{'name':'See Food'},{'name':'Non Veg'},{'name':'Snack'}],
        }
        res = self.client.post(RECIPES_URL,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes =models.Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(),1)
        recipe =recipes[0]
        self.assertEqual(recipe.tags.count(),3)
        self.assertIn(see_food_tag,recipe.tags.all())
        for tag in payload['tags']:
            exits = recipe.tags.filter(
                name=tag['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exits)
            
    def test_update_on_new_tag(self):
        ''' Testing update on new tag '''
        recipe = create_recipe(user= self.user)
        
        payload = {'tags':[{'name':'Breakfast'}]}
        
        url = detail_url(recipe)
        res = self.client.patch(url,payload,format="json")
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = models.Tag.objects.get(user=self.user, name='Breakfast')
        self.assertIn(new_tag, recipe.tags.all())
        
    def test_update_on_existing_tag(self):
        '''Testing update on existing tag'''
        dessert_tag = models.Tag.objects.create(user= self.user, name='Dessert')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(dessert_tag)
        
        dinner_tag =models.Tag.objects.create(user = self.user, name='Dinner')
        payload = {'tags':[{'name':'Dinner'}]}
        url = detail_url(recipe)
        res = self.client.patch(url, payload,format="json")
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(dinner_tag, recipe.tags.all())
        self.assertNotIn(dessert_tag, recipe.tags.all())
        
    def test_clear_tags(self):
        '''test for clearing tags'''
        tag = models.Tag.objects.create(user=self.user, name ='Cakes')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag)
        
        payload = {'tags' : []}
        url =detail_url(recipe)
        res = self.client.patch(url, payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(),0)
        
    def test_create_recipe_with_new_ingredients(self):
        ''' Test creating recipe with new ingredients'''
        
        payload ={
            'title':'chicken nuggets',
            'time_minutes':7,
            'price':Decimal('2.3'),
            'ingredients':[{'name':'chicken'},{'name':'sauce'}],
        }
        
        res = self.client.post(RECIPES_URL,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = models.Recipe.objects.filter(user =self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name = ingredient['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)
            
    def test_create_recipe_with_existing_ingredients(self):
        ''' Test existing recipe with new ingredients'''
        ghee_ingredient = models.Ingredients.objects.create(user=self.user,name='ghee')
        payload ={
            'title':'jalebi',
            'time_minutes':120,
            'price':Decimal('4.3'),
            'ingredients':[{'name':'ghee'},{'name':'maida'}],
        }
        
        res = self.client.post(RECIPES_URL,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = models.Recipe.objects.filter(user =self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        self.assertIn(ghee_ingredient,recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name = ingredient['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)
            
    def test_create_ingredient_on_update(self):
        '''Test creating ingredient on updating recipe'''
        
        recipe =create_recipe(user = self.user)
        
        payload = {'ingredients':[{'name':'Peanuts'}]}
        url = detail_url(recipe)
        res = self.client.patch(url, payload, format ='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        peanut_ingredient = models.Ingredients.objects.get(
            user = self.user,
            name ='Peanuts',
        )
        self.assertIn(peanut_ingredient, recipe.ingredients.all())
        
    def test_updating_ingredient(self):
        ''' updating ingredient on recipe updation'''
        butter_ingredient = models.Ingredients.objects.create(
            user = self.user,
            name = 'Butter',
        )
        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(butter_ingredient)
        
        ghee_ingredient = models.Ingredients.objects.create(
            user = self.user,
            name ='Ghee',
        )
        payload = {'ingredients':[{'name':'Ghee'}]}
        url =detail_url(recipe)
        res = self.client.patch(url, payload,format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ghee_ingredient, recipe.ingredients.all())
        self.assertNotIn(butter_ingredient, recipe.ingredients.all())
        
    def test_clear_ingredient(self):
        '''Test for clear ingredients'''
        ingredient = models.Ingredients.objects.create(
            user = self.user,
            name ='Sugar'
        )
        recipe = create_recipe(user =self.user)
        recipe.ingredients.add(ingredient)
        
        payload = {'ingredients':[]}
        url =detail_url(recipe)
        res = self.client.patch(url, payload,format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(),0)
        
class ImageUploadTests(TestCase):
    ''' Testing upload images'''
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email = 'test@gmail.com',
            password ='test123',
        )       
        
        self.client.force_authenticate(user = self.user)
        self.recipe = create_recipe(user = self.user)
        
    def tearDown(self):
        self.recipe.image.delete()
        
    def test_upload_image(self):
        '''Testing upload image'''
        
        url = image_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as img_file:
            img = Image.new('RGB',(10,10))
            img.save(img_file,format='JPEG')
            img_file.seek(0)
            payload = {'image':img_file}
            
            res =self.client.post(url,payload, format='multipart')
        
        self.recipe.refresh_from_db()    
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
        
    def test_upload_image_failed(self):
        '''Test upload image'''
        
        url = image_url(self.recipe.id)
        payload = {'image':'test-img'}
        
        res = self.client.post(url, payload,format='multipart')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
            
            
                                  
        
        
        
        
        
        
        
        