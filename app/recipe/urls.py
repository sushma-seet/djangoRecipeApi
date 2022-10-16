'''
urls for recipe
'''

from rest_framework.routers import DefaultRouter

from recipe import views

from django.urls import (
    path,include
)

router = DefaultRouter()
router.register('recipes',views.RecipeView)

app_name ='recipe'

urlpatterns = [
    path('',include(router.urls)),
]