'''
Tests for Tags API

'''

from _decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag,Recipe
from recipe.serializers import TagSerializer



TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    '''creating and return detail tag'''
    return reverse('recipe:tag-detail',args=[tag_id])


def create_user(email = 'test@example.com', password = 'test123'):
    '''' creating user '''
    
    return get_user_model().objects.create_user(email = email, password = password)


class PulicUserAPITests(TestCase):
    '''
    Testing unauthenticate user
    '''
    
    def setUp(self):
        self.client = APIClient()
        
    def test_unauthenticate_user(self):
        ''' Tests for unauthenticate user'''
        
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateTagsAPITests(TestCase):
    
    ''' Tests for authorized users'''
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        ''' Test for authorized user '''
        
        Tag.objects.create(user = self.user, name ='Veg')
        Tag.objects.create(user = self.user,name = 'Non Veg')
        
        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many =True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.assertEqual(res.data,serializer.data)
        
    def test_retrieve_limited_tags(self):
        '''
        Test for retrieving tags for current user
        '''
        user_2 = create_user(
            email='test2@gmail.com',
            password='test12345'
        )
        Tag.objects.create(user=user_2, name = 'Desserts')
        tag = Tag.objects.create(user= self.user, name='Salads')
        
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        
    def test_update_tag(self):
        ''' updating perticular tag'''
        
        tag = Tag.objects.create(
            user = self.user,
            name ='Pizzas'
        )
        
        payload = {'name':'Burgers'}
        url = detail_url(tag.id)
        
        res = self.client.patch(url,payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name,payload['name'])
        
    def test_delete_tag(self):
        ''' Self delete tag'''
        tag = Tag.objects.create(user= self.user, name="Pancake")
        
        url = detail_url(tag.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user =self.user)
        self.assertFalse(tags.exists())
        
    def test_filter_tags_assigned_to_recipe(self):
        ''' Test filter tags assigned to recipe'''
        
        tag_1 = Tag.objects.create(user =self.user, name ='starters')
        tag_2 = Tag.objects.create(user =self.user, name ='lunch')
        
        recipe = Recipe.objects.create(
            user =self.user,
            title ='fish fingers',
            time_minutes = 120,
            price = Decimal('6.2'),
        )
        
        recipe.tags.add(tag_1)
        
        res = self.client.get(TAGS_URL, {'assigned_only':1})
        
        serializer_1 = TagSerializer(tag_1)
        serializer_2 = TagSerializer(tag_2)
        
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)
        
        
    def test_filter_tags_unique(self):
        ''' Test filter unique tags'''
        tag_1 = Tag.objects.create(user = self.user, name ='breakfast')
        tag_2 = Tag.objects.create(user=self.user , name ='dinner')
        
        recipe_1 = Recipe.objects.create(
            user = self.user,
            title = 'edly',
            time_minutes = 40,
            price = Decimal('2.6'),
        )
        
        recipe_2 = Recipe.objects.create(
            user = self.user,
            title = 'bread and jam',
            time_minutes = 10,
            price = Decimal('1.2'),
        )
        
        recipe_1.tags.add(tag_1)
        recipe_2.tags.add(tag_1)
        
        res = self.client.get(TAGS_URL,{'assigned_only':1})
        
        self.assertEqual(len(res.data),1)
        
        
        