'''
Testing Models
'''

from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models



def create_user(email,password):
    return get_user_model().objects.create_user(email = email,password=password)

class ModelTests(TestCase):
    '''
    testing users models
    '''
    
    def test_create_user_successful_with_email(self):
        
        email = 'sushma.kalluri@gmail.com'
        password = 'sushma12345'
        
        user = create_user(email = email,password = password)
        
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
        user =create_user(
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
        
    def test_create_tag_model(self):
        '''
        testing creating tag model
        '''
        user = create_user(
            email='user@gmail.com',
            password = 'user123'
        )

        tag = models.Tag.objects.create(
            user = user,
            name = 'test tag'
        )

        self.assertEqual(str(tag),tag.name)
        
    def test_create_ingredient_model(self):
        '''
        testing creating ingredient model
        '''
        user = create_user(
            email='user@gmail.com',
            password = 'user123'
        )

        ingredient = models.Ingredients.objects.create(
            user = user,
            name = 'hot chocolate sauce'
        )

        self.assertEqual(str(ingredient),ingredient.name)
        
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self,mock_uuid):
        uuid ='test-uuid'    
        mock_uuid.return_value = uuid
        file_path =models.recipe_image_file_path(None,'test.jpg')
        
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
        
    def test_movie_model(self):
        
        user = create_user(
            email ='sushma.kalluri@gmail.com',
            password = 'sushma143',
        )
        
        movie = models.Movie.objects.create(
            user = user,
            name = 'Happy Days',
            release_date = '2007-10-02',
            ratings = Decimal(4.9),
            director = 'Shekar kammula',
            producer = 'Gary Marshall',
        )
        
        self.assertEqual(str(movie),movie.name)
        
    def test_character_model(self):
        '''Test for character model'''
        
        user = create_user(
            email = 'sushma.kalluri@gmail.com',
            password='pass1234',
        )
        
        characters = models.Characters.objects.create(
            user = user,
            name = 'Kattappa'
        )
        
        self.assertEqual(str(characters),characters.name)
        
        
        