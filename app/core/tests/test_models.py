'''
Testing Models
'''
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    '''
    testing users models
    '''
    
    def test_create_user_successful_with_email(self):
        
        email = 'sushma.kalluri@gmail.com'
        password = 'sushma12345'
        
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_normalize_emails(self):
        
        sample_emails = [
            ["sushma1@GMAIL.COM", "sushma1@gmail.com"],
            ["SUSHMA2@GMAIL.COM", "SUSHMA2@gmail.com"],
            ["Sushma3@GMAIL.COM", "Sushma3@gmail.com"],
            ["sushma4@gmail.COM", "sushma4@gmail.com"],
        ]
        
        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, 'sushma123')
            self.assertEqual(user.email,expected_email)
            
    def test_empty_email(self):
        '''
        raise value error with an empty email
        '''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','sushma123')
            
    def test_create_superuser(self):
        
        '''testing creating super user'''
        
        user = get_user_model().objects.create_superuser('sushma.kalluri@gmail.com', 'sushma@123')
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_create_recipe_successful(self):
        '''
        testing create recipe successful
        '''
        user =get_user_model().objects.create_user(
            email = 'sample@gmail.com',
            password = 'sample123',
        )
        
        recipe = models.Recipe.objects.create(
            user = user,
            title ='sample recipe',
            time_minutes = 10,
            price = Decimal('4.5'),
            description = 'this is the sample recipe.'
        )
        
        self.assertEqual(str(recipe),recipe.title)
        