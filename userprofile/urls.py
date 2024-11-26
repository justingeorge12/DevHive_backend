from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'userprofile', UserProfile, basename='userprofile')
# router.register(r'otheruserprofile/<int:user_id>/', OtherUserProfile, basename='otheruserprofile')



urlpatterns = [
    path('changepassword', ChangePassword.as_view(), name='changepassword'),
    path('userquestion', UserQuestionView.as_view(), name='userquestion'),
    path('useranswer', UserAnswerView.as_view(), name='useranswer'),
    path('usersaved', UserSavedView.as_view(), name='usersaved'),
    path('updateuserprofile', UserProfileUpdateView.as_view(), name='updateuserprofile'),
    path('userquestionanswer/<int:id>/', UserQuestionAnswerView.as_view(), name='userquestionanswer'),
    path('myaddress/<int:id>',AddressRetrieveUpdateView.as_view(), name='myaddress'),

    path('follow/<int:user_id>', FollowUserView.as_view(), name='follow'),
    path('unfollow/<int:user_id>', UnfollowUserView.as_view(), name='unfollow'),
    path('followers/<int:user_id>', FollowersListView.as_view(), name='followers'),
    path('following/<int:user_id>', FollowingListView.as_view(),  name='following'),
    path('userfollowcount/<str:username>', UserFollowCountsView.as_view(), name='userfollowcount'),
    path('userfollowcount', UserFollowCountsView.as_view(), name='userfollowcount'),
    path('isfollowing/<str:username>', IsFollowingView.as_view(), name='isfollowing'),

    path('otheruserprofile/<str:username>/', OtherUserProfile.as_view(), name='otheruserprofile'),
    path('searchuser/', SeachOtherUser.as_view(), name = 'searchuser' ),

    path('',include(router.urls)),

    
]
