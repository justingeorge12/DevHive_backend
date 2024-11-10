
from django.urls import path, include
from . views import *
from rest_framework_simplejwt.views import  TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'listusers',ListUsers, basename='listuser')
router.register(r'listtags',ListTags, basename='listtags')

urlpatterns = [

    path('register', CreateUserView.as_view(), name = 'register'),
    path('token', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name='refresh'),
    path('resendotp', ResendOtpView.as_view(), name='resendotp'),
    path('otp', OtpView.as_view(), name='otp'),
    path('getemail',getEmail.as_view(), name='getemail'),
    path('forgetpass', forgetPasswor.as_view(), name='forgetpass'),
    path('logout',Logout.as_view(), name='logout' ),

    path('deleteuserquestion/<int:id>', DeleteUserQuestion.as_view(), name='deleteuserquestion'),
    path('updatequestion/<int:id>', QuestionUpdateView.as_view(), name='updatequestion'),
    path('acceptanswer/<int:question_id>/<int:answer_id>', AcceptAnswerView.as_view(), name='acceptanswer'),

    path('google', GoogleSignInView.as_view(), name='google'),

    path('',include(router.urls)),











    # path('home/', HomeView.as_view(), name ='home'),
    # path('logout/', views.LogoutView.as_view(), name ='logout'),
]