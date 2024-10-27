from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import * 
from .serializer import TagSerializer, UserRetriUpdate
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from user.models import Users

from QA.serializer import QuestionSerializer, AnswerSerializer
from QA.models import Question, Answers

# Create your views here.

class ManageTag(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserList(ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UserRetriUpdate
    def get_queryset(self):
        return Users.objects.filter(is_superuser=False)

class UserManage(RetrieveUpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserRetriUpdate
    lookup_field = 'id'
    def get_queryset(self):
        return Users.objects.filter(is_superuser=False)

class ListQuestions(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.all()
    

class ListAnswers(ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.all()
    