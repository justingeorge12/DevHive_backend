from django.urls import path
from .views import *

urlpatterns = [
    path('chathistory/<int:receiver_id>',ChatHistorysView.as_view(), name='chathistory' ),
    path('chatuserslist/', ChatUserListView.as_view(), name='chatuserslist'),
    path('specificuser/<int:user_id>', specificUserDetails.as_view(), name='specificuser'),
]
