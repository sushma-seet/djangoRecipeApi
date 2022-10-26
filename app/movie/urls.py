'''
urls for movie APIs
'''

from django.urls import path,include


from movie import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('movie', views.MovieView)
router.register('character', views.CharacterView)

app_name ='movie'

urlpatterns = [
    path(' ',include(router.urls))
]


