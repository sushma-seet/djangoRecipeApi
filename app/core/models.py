'''
Models

'''

from distutils.command import upload
from pydoc import describe
import uuid
import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


def recipe_image_file_path(instance, filename):
    ''' generating image filepath'''
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    
    return os.path.join('uploads','recipe', filename)


class UserManager(BaseUserManager):
    
    ''' manage users'''
    
    def create_user(self, email, password = None, **extra_fields):
        
        if not email:
            raise ValueError('user must have an email')
        user = self.model(email =self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,email,password):
        '''creating super users'''
        
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        
        return user

class User(AbstractBaseUser, PermissionsMixin):
    '''
    User Fields
    '''
    email = models.EmailField(unique = True,max_length = 255)
    name = models.CharField(max_length = 255)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    

class Recipe(models.Model):
    ''''
    model for recipe app
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )
    title =models.CharField(max_length =255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits =5,decimal_places =2)
    link = models.CharField(max_length = 255,blank=True)
    description = models.TextField(blank =True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredients')
    image = models.ImageField(null =True, upload_to =recipe_image_file_path)
    
    
    def __str__(self):
        return self.title
    
class Tag(models.Model):
    '''
    create tag model
    '''
    
    name = models.CharField(max_length = 255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    
    def __str__(self):
        return self.name
    
class Ingredients(models.Model):
    '''
    create ingredients model
    '''
    name = models.CharField(max_length = 255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    
    
    def __str__(self):
        return self.name
    
    
class Makeup(models.Model):
    '''
    model for makeup app
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    
    name = models.CharField(max_length =255)
    cost = models.IntegerField()
    time = models.IntegerField()
    description = models.TextField()
    
    
    def __str__(self):
        return self.name
    
class Movie(models.Model):
    '''
    customized model for practice
    '''
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    
    name = models.CharField(max_length = 255)
    release_date = models.DateField()
    ratings = models.DecimalField(max_digits =6,decimal_places =2)
    director = models.CharField(max_length = 255,blank=True)
    producer = models.CharField(max_length = 255,blank=True)
    characters = models.ManyToManyField('Characters')
    
    def __str__(self):
        return self.name
        
        
class Characters(models.Model):
    
    '''
    characters for movies
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    name = models.CharField(max_length = 255)
    
    def __str__(self):
        return self.name
    
    
    
    
    


