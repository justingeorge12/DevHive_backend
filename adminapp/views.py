from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import * 
from .serializer import TagSerializer, UserRetriUpdate
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import filters
from rest_framework.permissions import AllowAny

from user.models import Users
from user.serializers import UserSerializer

from QA.serializer import QuestionSerializer, AnswerSerializer
from QA.models import Question, Answers

from rewards.models import Product
from rewards.serializers import ProductSerializer

from .permission import IsSuperUser
from QA.pagination import AdminListPagination



# Create your views here.

class ManageTag(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer
    pagination_class = AdminListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Tag.objects.all().order_by('-id')
        search = self.request.query_params.get('search', None)
        print(queryset, '-----------------------------')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    


class UserList(ListAPIView):
    # queryset = Users.objects.all()
    serializer_class = UserRetriUpdate
    pagination_class = AdminListPagination 
    def get_queryset(self):
        queryset = Users.objects.filter(is_superuser=False).order_by('-id')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(username__icontains=search)
        return queryset

class UserManage(RetrieveUpdateAPIView):
    queryset = Users.objects.all().order_by('-id')
    serializer_class = UserRetriUpdate
    lookup_field = 'id'
    def get_queryset(self):
        return Users.objects.filter(is_superuser=False)

class ListQuestions(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset =  Question.objects.all().order_by('-id')
        search = self.request.query_params.get('search', None)

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

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



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsSuperUser]


    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # def perform_create(self, serializer):
    #     serializer.save()