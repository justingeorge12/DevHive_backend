from django.urls import path
from .views import *

urlpatterns = [
    path('chathistory/<int:receiver_id>',ChatHistorysView.as_view(), name='chathistory' )
]
