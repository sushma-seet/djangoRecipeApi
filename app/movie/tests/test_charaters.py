'''
Tests for adding Character to Movie
'''

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Characters
from movie.serializers import CharacterSerializer


CHARACTER_URL  = reverse('movie:characters-list')

def create_user(email = "test@gmail.com",password="pass123"):
    ''' creating user for test cases'''
    return get_user_model().objects.create_user(
        email = email,
        password = password
    )


class PublicUserTests(TestCase):
    '''Test get list of character with unauthorized user '''
    
    def setUp(self):
        self.client = APIClient()
        
    def test_get_character_list(self):
        '''test geting list of character '''
        
        res = self.client.get(CHARACTER_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateUserTests(TestCase):
    '''Test get list of character with authorized user '''
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user = self.user)
        
    def test_get_character_list(self):
        '''test geting list of character '''
        Characters.objects.create(
            user = self.user,
            name = 'Ballala Deva'
        )
        
        res = self.client.get(CHARACTER_URL)
        
        characters = Characters.objects.all().order_by('-name')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = CharacterSerializer(characters)
        # self.assertEqual(res.data, serializer.data)
        
    def test_get_character_limited(self):
        '''test geting list of character limites to users'''
        
        another_user = create_user(
            email='test_2@gmail.com',
            password ='pass123456'
        )
        
        character = Characters.objects.create(
            user = another_user,
            name = 'Ballala Deva'
        )
        character_2 = Characters.objects.create(
            user = self.user,
            name = 'Devasena'
        )
        
        res = self.client.get(CHARACTER_URL)
        
        actual_characters = Characters.objects.all().order_by('-name')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = CharacterSerializer(actual_characters)
        self.assertEqual(len(res.data),1)
        

        