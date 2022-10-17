'''
Tests for Tags API

'''

from genericpath import exists
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
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
        
        
        