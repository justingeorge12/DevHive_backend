from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import * 
from .serializer import TagSerializer, UserRetriUpdate
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView

from user.models import Users
from user.serializers import UserSerializer

from QA.serializer import QuestionSerializer, AnswerSerializer
from QA.models import Question, Answers



# Create your views here.

class ManageTag(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer


class UserList(ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UserRetriUpdate
    def get_queryset(self):
        return Users.objects.filter(is_superuser=False).order_by('-id')

class UserManage(RetrieveUpdateAPIView):
    queryset = Users.objects.all().order_by('-id')
    serializer_class = UserRetriUpdate
    lookup_field = 'id'
    def get_queryset(self):
        return Users.objects.filter(is_superuser=False)

class ListQuestions(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.all().order_by('-id')
    

class ListAnswers(ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.all()
    

class AdminQuestionDetailView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class =  QuestionSerializer
    lookup_field='id'


class AdminQuestionAnswerView(ListAPIView):
    serializer_class = AnswerSerializer
    def get_queryset(self):
        question_id = self.kwargs.get('id')
        return  Answers.objects.filter(question_id=question_id)
    

class DeleteQuestionView(DestroyAPIView):
    queryset = Question.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        question_id = kwargs.get('id')
        print(f"Deleting question with ID: {question_id}")
        return super().delete(request, *args, **kwargs)
    

class DeleteAnswerView(DestroyAPIView):
    queryset = Answers.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        answer_id = kwargs.get('id')
        answer = self.get_object()
        question = answer.question
        if question:
            question.answer_count = max(0, question.answer_count - 1) 
            question.save()
        print(f'Deleting answer with id: {answer_id}')
        return super().delete(request, *args, **kwargs)
    


class BlockUserView(UpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_blocked = not user.is_blocked
        user.is_active = not user.is_active
        user.save()

        status_message = "blocked" if user.is_blocked else "unblocked"
        return Response({"message": f"User has been {status_message} successfully."},status=status.HTTP_200_OK)

