'''
seriazers for users
'''

from django.contrib.auth import get_user_model,authenticate
from django.utils.translation import gettext_lazy as translate

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model =get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password': {'write_only':True,'min_length':5}}
        
    def create(self, validate_data):
        return get_user_model().objects.create_user(**validate_data)
    
    def update(self,instance,validate_data):
        '''update and return user'''
        
        password = validate_data.pop('password',None)
        user =super().update(instance,validate_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    

class TokenSerializer(serializers.Serializer):
    '''
    Creating Serializer for our token authentication
    '''
    
    email = serializers.EmailField()
    password = serializers.CharField(
        style ={'input_type':'password'},
        trim_whitespace = False
        ) 
    
    def validate(self,args):
        email = args.get('email')
        password = args.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username = email,
            password= password,
        )
        
        if not user:
            message = translate('Unable authenticate with these credentials')
            raise serializers.ValidationError(message, code='authorization')
        
        args['user'] = user
        return args
    