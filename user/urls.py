
from django.urls import path, include
from . views import *
from rest_framework_simplejwt.views import  TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'listusers',ListUsers, basename='listuser')
router.register(r'listtags',ListTags, basename='listtags')
router.register(r'userprofile', UserProfile, basename='userprofile')

urlpatterns = [

    path('register', CreateUserView.as_view(), name = 'register'),
    path('token', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name='refresh'),
    path('resendotp', ResendOtpView.as_view(), name='resendotp'),
    path('otp', OtpView.as_view(), name='otp'),
    path('getemail',getEmail.as_view(), name='getemail'),
    path('forgetpass', forgetPasswor.as_view(), name='forgetpass'),
    path('logout',Logout.as_view(), name='logout' ),

    path('userquestion', UserQuestionView.as_view(), name='userquestion'),
    path('useranswer', UserAnswerView.as_view(), name='useranswer'),
    path('updateuserprofile', UserProfileUpdateView.as_view(), name='updateuserprofile'),
    path('google/', GoogleSignInView.as_view(), name='google'),

    path('',include(router.urls)),











    # path('home/', HomeView.as_view(), name ='home'),
    # path('logout/', views.LogoutView.as_view(), name ='logout'),
]