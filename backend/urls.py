from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('',include('user.urls')),
    path('', include('adminapp.urls')),
]







# from django.contrib import admin
# from django.urls import path, include
# from rest_framework_simplejwt import views as jwt_views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
#     path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),

#     path('', include('user.urls')),
# ]
