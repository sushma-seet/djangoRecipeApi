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
router.register('tags',views.TageView)
router.register('ingredients',views.IngredientView)

app_name ='recipe'

urlpatterns = [
    path('',include(router.urls)),
]