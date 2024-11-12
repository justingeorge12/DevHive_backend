from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('',include('user.urls')),
    path('', include('adminapp.urls')),
    path('', include('QA.urls')),
    path('', include('userprofile.urls')),
    path('', include('chatapp.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







# from django.contrib import admin
# from django.urls import path, include
# from rest_framework_simplejwt import views as jwt_views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
#     path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),

#     path('', include('user.urls')),
# ]
