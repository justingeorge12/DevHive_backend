from django.urls import path
from .views import *

urlpatterns = [

    path('questionlist', QuestionListCreateAPIView.as_view(), name='queestionlist'),
    path('questionmanage/<int:id>/', QuestionRetrieveUpdateDestroyAPIView.as_view(), name='questionmanage'),
    path('questiontags/', ListTags.as_view(), name='listtags'),
    path('addlistanswer', AnswerListCreateAPIView.as_view(), name='addlistanswer'),
    path('managequesvote', handle_vote, name='managequesvote'),
    path('savequestion', handleSave, name='savequestion'),
    path('manageanswervote', handle_answer_vote, name='manageanswervote'),
    path('saveanswer', handleAnswerSave, name='savequestion'),
    path('elasticsearchquestion', SearchQuestions, name='elasticsearchquestion')
    
]



