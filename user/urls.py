
from django.urls import path
from . views import *
from rest_framework_simplejwt.views import  TokenRefreshView


urlpatterns = [

    path('register', CreateUserView.as_view(), name = 'register'),
    path('token', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name='refresh'),
    path('resendotp', ResendOtpView.as_view(), name='resendotp'),
    path('otp', OtpView.as_view(), name='otp'),
    path('getemail',getEmail.as_view(), name='getemail'),
    path('forgetpass', forgetPasswor.as_view(), name='forgetpass')











    # path('home/', HomeView.as_view(), name ='home'),
    # path('logout/', views.LogoutView.as_view(), name ='logout'),
]