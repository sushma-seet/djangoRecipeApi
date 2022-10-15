'''
Models

'''
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


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
    
    
    


