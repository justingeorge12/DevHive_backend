
from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'tags', ManageTag, basename= 'tags')

urlpatterns = [
    path('', include(router.urls)), 
    path('usermanage',UserList.as_view(), name='usermanage'),
    path('usermanage/<int:id>',UserManage.as_view(), name='usermanage'),
    
]
