'''
Tests for user api

'''

import email
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    '''
    Test class for users
    
    '''
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_user_success(self):
        '''
        test user created successfully
        '''
        payload = {
            'email' : 'sushmareddy@gmail.com',
            'password' : 'pass123',
            'name':'sushma',
        }
        
        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(email = payload['email'])
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)
        
    def test_user_already_exists(self):
        '''
        user already exists
        '''
        payload = {
            'email' : 'sushmareddy@gmail.com',
            'password' : 'pass123',
            'name':'sushma',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
    def test_password_too_short(self):
        '''
        password too short test
        '''
        payload = {
            'email' : 'sushmareddy@gmail.com',
            'password' : 'ps',
            'name':'sushma',
        }
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()
        
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_create_token_bad_credentials(self):
        '''
        Testing Create token with invalid credentials
        '''
        users_details = {
            'email':'sushma.kalluri4@gmail.com',
            'password':'sushma123',
            'name':'sushma',
        }
        
        create_user(**users_details)
        payload = {
            'email':users_details['email'],
            'password':'pinky123',
        }
        res =self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_blank_password(self):
        '''
        Testing create token with blank password
        '''
        payload = {
            'email':'test@example.com',
            'password':'',
        }
        
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_user_unauthorize(self):
        '''
        retrieving user unauthorized
        '''
        res = self.client.post(ME_URL,{})
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateUserAPITests(TestCase):
    '''
    test API requests thats required authorizations
    '''
    
    def setUp(self):
        self.user = create_user(
            email='sushma123@gmail.com',
            password= 'sushma123',
            name = 'sushma',
        )
        self.client = APIClient()
        self.client.force_authenticate(user = self.user)
        
    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code,   status.HTTP_200_OK)
        self.assertEqual(
            res.data, {
                'name':self.user.name,
                'email':self.user.email,
            }
        )
        
    def test_post_me_not_allowed(self):
        
        res = self.client.post(ME_URL,{})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_update_user_profile(self):
        '''
        Testing update user profile
        '''
        
        payoad = {
            'email':'new@gmail.com'
            }
        res = self.client.patch(ME_URL,payoad)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payoad['email'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        