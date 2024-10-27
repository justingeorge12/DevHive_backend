from django.shortcuts import render

from rest_framework import generics
from .models import Question
from .serializer import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from adminapp.models import Tag
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import api_view

class QuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer  

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        print(context, 'cooooooooooooooooooooooooooooooooooooo')
        return context 
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    


class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    lookup_field = 'id'

class ListTags(generics.ListAPIView):
    # permission_classes = [AllowAny]
    serializer_class = TagSerializer
    
    def get_queryset(self):
        tag = self.request.query_params.get('letter', None)

        if tag:
            return Tag.objects.filter(name__istartswith=tag).order_by('name')
        
        return Tag.objects.none()
    

class AnswerListCreateAPIView(generics.ListCreateAPIView):
    queryset = Answers.objects.all()
    serializer_class = AnswerSerializer 

    def perform_create(self, serializer):
        answer = serializer.save(user=self.request.user)
        question = answer.question
        question.answer_count += 1
        question.save()

        user = self.request.user
        user.coins += 10 
        user.save()

    def get_queryset(self):
        question_id = self.request.query_params.get('question_id', None)
        
        if question_id is None:
            raise ValidationError({'detail': 'question id is required'})
        
        return Answers.objects.filter(question_id=question_id) 


@api_view(['POST'])
def handle_vote(request):
    user = request.user
    question_id = request.data.get('question_id')
    vote_type = request.data.get('vote_type')

    question = Question.objects.get(id = question_id)
    print(question_id, '---------------------------------------------------------------')

    vote = QuestionVotes.objects.filter(user=user, question=question).first()

    if vote:
        if vote.vote_type == vote_type:
            vote.delete()
            if vote_type == 'upvote':
                question.pos_vote -= 1
            elif vote_type == 'downvote':
                question.neg_vote -= 1
        
        else:
            vote.vote_type = vote_type
            vote.save()
            if vote_type == 'upvote':
                question.pos_vote += 1
            elif vote_type == 'downvote':
                question.neg_vote += 1
    else:
        QuestionVotes.objects.create(user=user, question=question, vote_type= vote_type)
        if vote_type == 'upvote':
            question.pos_vote += 1
        elif vote_type == 'downvote':
            question.neg_vote += 1
    question.save()

    upvotes = QuestionVotes.objects.filter(question=question, vote_type='upvote').count()
    downvotes = QuestionVotes.objects.filter(question=question, vote_type='downvote').count()

    return Response({'upvotes': upvotes, 'downvotes': downvotes, 'user_vote': vote_type })


@api_view(['POST'])
def handleSave(request):
    user = request.user
    question_id = request.data.get('question_id')
    question = Question.objects.get(id = question_id)

    saved = SavedQuestion.objects.filter(user=user, question = question)

    if not saved:
        SavedQuestion.objects.create(user=user, question=question)
        return Response('your qustion is saved successfully ')
    else:
        return Response('you are already saved this question')
