from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField

from rest_framework import generics, status
from .models import Question
from .serializer import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from adminapp.models import Tag
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .pagination import InfiniteScrollPagination
from .documents import QuestionDocument


class QuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Question.objects.all().order_by('-pos_vote')
    serializer_class = QuestionSerializer  
    pagination_class = InfiniteScrollPagination


    def get_queryset(self):
        filter_option = self.request.query_params.get('filter', 'votes')  

        
        if filter_option == 'newest':
            return Question.objects.all().order_by('-id') 
        elif filter_option == 'alphabet':
            return Question.objects.all().order_by('title')
        if filter_option == 'answered':
            return Question.objects.filter(answer_count__gt=0).order_by('-created')
        elif filter_option == 'unanswered':
            return Question.objects.filter(answer_count=0).order_by('-created')
        elif filter_option == 'accepted':
            return Question.objects.filter(accepted=True).order_by('-created')
        else:
            return Question.objects.all().order_by('-pos_vote')
        

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context 
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    


class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    lookup_field = 'id'

class ListTags(generics.ListAPIView):
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

        # user = self.request.user
        # user.coins += 10 
        # user.save()

    def get_queryset(self):
        question_id = self.request.query_params.get('question_id', None)
        
        if question_id is None:
            raise ValidationError({'detail': 'question id is required'})
        
        return Answers.objects.filter(question_id=question_id).order_by('accepted').order_by('-pos_vote')


@api_view(['POST'])
def handle_vote(request):
    user = request.user
    question_id = request.data.get('question_id')
    vote_type = request.data.get('vote_type')

    question = Question.objects.get(id = question_id)

    if question.user == user:
        return Response({'detail': "You cannot vote on your own question."}, status=403)


    vote = QuestionVotes.objects.filter(user=user, question=question).first()

    if vote:
        if vote.vote_type == vote_type:
            vote.delete()
            if vote_type == 'upvote':
                question.pos_vote -= 1
                question.user.coins -= 2
                question.user.total_votes -= 1
            elif vote_type == 'downvote':
                question.neg_vote -= 1
                question.user.total_votes += 1
        
        else:
            vote.vote_type = vote_type
            vote.save()
            if vote_type == 'upvote':
                question.pos_vote += 1
                question.neg_vote -= 1
                question.user.coins += 2
                question.user.total_votes += 2
            elif vote_type == 'downvote':
                question.neg_vote += 1
                question.pos_vote -= 1
                question.user.coins -= 2
                question.user.total_votes -= 2
    else:
        QuestionVotes.objects.create(user=user, question=question, vote_type= vote_type)
        if vote_type == 'upvote':
            question.pos_vote += 1
            question.user.coins += 2
            question.user.total_votes += 1
            print(question.user, '...........', question.user.total_votes)

        elif vote_type == 'downvote':
            question.neg_vote += 1
            question.user.total_votes -= 1
            print(question.user, '...........', question.user.total_votes)
    question.save()
    question.user.save()

    upvotes = QuestionVotes.objects.filter(question=question, vote_type='upvote').count()
    downvotes = QuestionVotes.objects.filter(question=question, vote_type='downvote').count()
    votedQuestion = Question.objects.get(id = question_id)
    return Response({'upvotes': upvotes, 'downvotes': downvotes, 'user_vote': vote_type, 'tot_posvote':votedQuestion.pos_vote, 'tot_negvote':votedQuestion.neg_vote})


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





@api_view(['POST'])
def handle_answer_vote(request):
    user = request.user
    answer_id = request.data.get('answer_id')
    vote_type = request.data.get('vote_type')

    answer = Answers.objects.get(id = answer_id)

    if answer.user == user:
        return Response({'detail': "You cannot vote on your own answer."}, status=403)


    vote = AnswerVotes.objects.filter(user=user, answer=answer).first()

    if vote:
        if vote.vote_type == vote_type:
            vote.delete()
            if vote_type == 'upvote':
                answer.pos_vote -= 1
                answer.user.coins -= 2
                answer.user.total_votes -= 1
            elif vote_type == 'downvote':
                answer.neg_vote -= 1
                answer.user.total_votes += 1
        
        else:
            vote.vote_type = vote_type
            vote.save()
            if vote_type == 'upvote':
                answer.pos_vote += 1
                answer.neg_vote -= 1
                answer.user.coins += 2
                answer.user.total_votes += 2
            elif vote_type == 'downvote':
                answer.neg_vote += 1
                answer.pos_vote -= 1
                answer.user.coins -= 2
                answer.user.total_votes -= 2
    else:
        AnswerVotes.objects.create(user=user, answer=answer, vote_type= vote_type)
        if vote_type == 'upvote':
            answer.pos_vote += 1
            answer.user.coins += 2
            answer.user.total_votes += 1
        elif vote_type == 'downvote':
            answer.neg_vote += 1
            answer.user.total_votes -= 1
    answer.save()
    answer.user.save()

    upvotes = AnswerVotes.objects.filter(answer=answer, vote_type='upvote').count()
    downvotes = AnswerVotes.objects.filter(answer=answer, vote_type='downvote').count()

    votedAnswer = Answers.objects.get(id=answer_id)

    return Response({'upvotes': upvotes, 'downvotes': downvotes, 'user_vote': vote_type, 'pos_vote':votedAnswer.pos_vote, 'neg_vote':votedAnswer.neg_vote })




@api_view(['POST'])
def handleAnswerSave(request):
    user = request.user
    question_id = request.data.get('question_id')
    answer_id = request.data.get('answer_id')
    answer = Answers.objects.get(id = answer_id)
    question = Question.objects.get(id = question_id)

    saved = SavedAnswer.objects.filter(user=user, answer = answer, question = question)

    if not saved:
        SavedAnswer.objects.create(user=user, answer=answer, question=question)
        return Response('your answer is saved successfully ')
    else:
        return Response('you are already saved this answer')


# def SearchQuestions(request):
#     query = request.GET.get('q')
#     if query:
#         questions = QuestionDocument.search().query("multi_match", query=query, fields=['title'])
#         results = questions.to_queryset()
#         print(results, '--------------------------------------------------------------------------------------')
#     else:
#         results = Question.objects.none()
#     return JsonResponse({"results": list(results.values('id','title', 'body', 'created', 'pos_vote', 'neg_vote', 'user', 'accepted', 'answer_count', 'tags', 'closed'))})


def SearchQuestions(request):
    query = request.GET.get('q')
    
    if query:
        questions = QuestionDocument.search().query("multi_match", query=query, fields=['title'])
        question_ids = [hit.meta.id for hit in questions]

        ordering = Case(*[When(id=question_id, then=Value(index)) for index, question_id in enumerate(question_ids)], default=Value(len(question_ids)), output_field=IntegerField())
        results = Question.objects.filter(id__in=question_ids).select_related('user').prefetch_related('tags').order_by(ordering)

    else:
        results = Question.objects.none()
    
    response_data = []
    for question in results:
        profile_url = request.build_absolute_uri(question.user.profile.url) if question.user.profile else None

        question_data = {
            "id": question.id,
            "title": question.title,
            "body": question.body,
            "created": question.created,
            "pos_vote": question.pos_vote,
            "neg_vote": question.neg_vote,
            "user": {
                "id": question.user.id,
                "username": question.user.username, 
                "profile": profile_url,
                "total_votes":question.user.total_votes
            },
            "accepted": question.accepted,
            "answer_count": question.answer_count,
            "tags": [tag.name for tag in question.tags.all()],
            "closed": question.closed
        }
        response_data.append(question_data)
    
    return JsonResponse({"results": response_data})
