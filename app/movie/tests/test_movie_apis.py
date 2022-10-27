'''
Test for Movie APIs
'''


from rest_framework.test import APIClient
from rest_framework import status

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model
from core import models
from movie.serializers import MovieSerializer,MovieDetailSerializer


MOVIE_URL  = reverse('movie:movie-list')

def detail_url(movie_id):
    return reverse('movie:movie-detail',args=[movie_id])

def create_user(email = 'test@gmail.com',password = 'test123'):
    ''' Creating user for test'''
    return get_user_model().objects.create(
        email = email,
        password = password
    )
    
def create_movie(user, **movie_object):
    
    sample_object = {
        "name" :'Vampire Diaries',
        "release_date" : '2009-09-10',
        "ratings" : Decimal(4.8),
        "director" : 'John Behring',
        "producer" : 'kevin williamson',
    }
    
    sample_object.update(movie_object)
    movie = models.Movie.objects.create(
        user = user,
        **sample_object
    )
    return movie
    
    
    
class PublicUserTests(TestCase):
    ''' Class to test unauthorized users'''
    
    def setUp(self):
        self.client = APIClient()
        
    def test_get_movie_list(self):
        
        res = self.client.get(MOVIE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateUserTests(TestCase):
    ''' Tests With authorized users'''
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user = self.user)
        
    def test_get_movie_list(self):
        '''Test get list of movies'''
        
        movie = create_movie(user=self.user)
        
        res = self.client.get(MOVIE_URL)
        
        movies = models.Movie.objects.all().order_by('-id')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = MovieSerializer(movies, many =True)
        self.assertEqual(res.data,serializer.data)
        
    def test_get_movie_list_limited(self):
        '''Test get list of movies for authorized user'''
        
        other_user = create_user(
            email = 'sample@gmail.com',
            password='pass123',
        )
        movie = create_movie(user=self.user)
        movie_2 = create_movie(user=other_user)
        
        res = self.client.get(MOVIE_URL)
        
        movies = models.Movie.objects.filter(user =self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = MovieSerializer(movies, many =True)
        self.assertEqual(res.data,serializer.data)
        
    def test_create_movie(self):
        '''test create movie'''
        sample_movie = {
            'name': 'sample movie',
            'release_date':'2022-10-01',
            'ratings':Decimal('3.1'),
            'user':self.user
        }
        
        res = self.client.post(MOVIE_URL,sample_movie)
        
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = models.Movie.objects.get(id = res.data['id'])
        self.assertEqual(movie.user, self.user)
        
    
    def test_get_movie(self):
        '''Test get movie based on id '''
        movie = create_movie(user=self.user)
        
        url = detail_url(movie.id)
        res = self.client.get(url)
        
        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_partial_update(self):
        ''' Test updating movie'''
        
        movie = create_movie(user = self.user)
        
        payload = {'name':'new movie'}
        url = detail_url(movie.id)
        res = self.client.patch(url, payload)
        
        movie.refresh_from_db()
        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_full_update(self):
        ''' Test put movie'''
        
        movie = create_movie(user = self.user)
        
        payload = {
            'name':'new movie',
            'release_date':'2022-01-01',
            'ratings':Decimal('3.1')
            }
        url = detail_url(movie.id)
        res = self.client.put(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        movie.refresh_from_db()
        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.data, serializer.data)
        
    def test_delete_movie(self):
        ''' Test delete movie'''
        
        movie = create_movie(user = self.user)
        
        url = detail_url(movie.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_create_movie_with_new_characters(self):
        
        ''' Test creating new character with movie'''
        
        payload = {
            'name':'Magadheera',
            'release_date':'2004-09-21',
            'ratings':Decimal('4.5'),
            'characters' :[{'name':'Kalabirava'},{'name':'mithravinda'}]
            }
        
        res = self.client.post(MOVIE_URL, payload ,format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movies = models.Movie.objects.filter(user = self.user)
        movie = movies[0]
        self.assertEqual(movie.characters.count(),2)
        for character in payload['characters']:
            character = models.Characters.objects.filter(
                user = self.user,
                name = character['name']
            ).exists()
            self.assertTrue(character)
            
    def test_create_movie_with_existing_characters(self):
        
        ''' Test creating existing character with movie'''
        
        character = models.Characters.objects.create(
            user = self.user,
            name = 'Arundhathi'
        )
        payload = {
            'name':'Magadheera',
            'release_date':'2004-09-21',
            'ratings':Decimal('4.5'),
            'characters' :[{'name':'Arundhathi'},{'name':'Pashupathi'}]
            }
        
        res = self.client.post(MOVIE_URL, payload ,format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movies = models.Movie.objects.filter(user = self.user)
        movie = movies[0]
        self.assertEqual(movie.characters.count(),2)
        self.assertIn(character,movie.characters.all())
        for character in payload['characters']:
            character = models.Characters.objects.filter(
                user = self.user,
                name = character['name']
            ).exists()
            self.assertTrue(character)
            
    def test_create_characters_with_update(self):
        ''' Adding character while movie update'''
        movie = create_movie(user =self.user)
        
        payload = {'characters':[{'name':'Aravinda'}]}
        url =detail_url(movie.id)
        
        res = self.client.patch(url, payload, format ='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        character = models.Characters.objects.get(user = self.user, name ='Aravinda')
        self.assertIn(character,movie.characters.all())
        
    def test_assign_character_with_updating_movie(self):
        ''' Assign character while movie update'''
        movie = create_movie(user =self.user)
        character = models.Characters.objects.create(user=self.user, name = "Rudramadhevi")
        movie.characters.add(character)
        
        payload = {'characters':[{'name':'Anushka'}]}
        character_2 = models.Characters.objects.create(user=self.user, name = "Anushka")
        url =detail_url(movie.id)
        
        res = self.client.patch(url, payload, format ='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(character_2,movie.characters.all())
        self.assertNotIn(character,movie.characters.all())
        
    def test_delete_updating_movie(self):
        ''' delete character while movie update'''
        movie = create_movie(user =self.user)
        character = models.Characters.objects.create(user=self.user, name = "Rudramadhevi")
        movie.characters.add(character)
        
        payload = {'characters':[]}
        url =detail_url(movie.id)
        
        res = self.client.patch(url, payload, format ='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(movie.characters.count(),0)
        
        
        