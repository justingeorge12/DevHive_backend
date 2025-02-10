from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework import filters
from .serializers import UserSerializer, ListUsersSeralizer,  CustomTokenObtainPairSerializer
from .SocialSerializer.socialserializer import GoogleSignInSerializer
from .models import Users
from adminapp.models import Tag
from adminapp.serializer import TagSerializer

from .signal import generate_otp, send_otp_email

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from rest_framework.generics import ListAPIView, DestroyAPIView

from QA.serializer import QuestionSerializer, AnswerSerializer, SavedQuestionSerializer
from QA.models import Question, Answers, SavedQuestion

from .utils import register_social_user
from django.shortcuts import get_object_or_404






# for creating a new user
class CreateUserView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# Custom JWT token authentication view
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# API to resend OTP for email verification
class ResendOtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(data='email is required', status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Users.objects.get(email = email)
        except Users.DoesNotExist:
            return Response(data='user is not found', status=status.HTTP_404_NOT_FOUND)
        
        otp = generate_otp()
        user.otp = otp
        user.save()

        send_otp_email(email,user.username, otp)

        return Response(data='OTP resend successfull' , status=status.HTTP_200_OK)


#  to verify OTP and activate the user
class OtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        typedOtp = request.data.get('otp')

        if not email or not typedOtp:
            return Response(data='Email and Otp is required', status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Users.objects.get(email = email)
        except Users.DoesNotExist:
            return Response(data='User is not found', status=status.HTTP_404_NOT_FOUND)
        
        if not user.otp:
            return Response(data='OTP is expired', status=status.HTTP_400_BAD_REQUEST)
        
        storedOtp = user.otp
        if storedOtp == typedOtp:
            user.is_verified = True
            user.otp = None
            user.save()
            return Response(data='You are verified', status=status.HTTP_200_OK)
        else:
            return Response(data='invalid Otp ', status=status.HTTP_400_BAD_REQUEST)
        
#  check if an email exist
class getEmail(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        email = request.GET.get('email')
        user = Users.objects.filter(email=email, is_superuser = False).exists()
        if user:
            return Response(data='user exists', status=status.HTTP_200_OK)
        else:
            return Response(data='user is not exists', status=status.HTTP_404_NOT_FOUND)
        
# API to reset user password
class forgetPasswor(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = Users.objects.get(email = email)
        user.set_password(password)
        user.save()

        otp = generate_otp()
        user.otp = otp
        user.save()

        send_otp_email(email, user.username, otp)
        return Response(data='password has changed', status=status.HTTP_200_OK)
    
#  log out a user and blacklist token
class Logout(APIView):
    def post(self, request):
        try:
            refresh = request.data['token']
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        
# list all users
class ListUsers(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name']

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        
        if search:
            return Users.objects.filter(is_superuser=False, username__istartswith=search)
        else:
            return Users.objects.filter(is_superuser = False).order_by('-total_votes')
    
  
# list all tags
class ListTags(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


#  handle Google sign-in authentication
class GoogleSignInView(GenericAPIView):
    serializer_class=GoogleSignInSerializer
    permission_classes = [AllowAny]


    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)

        data = serializers.validated_data


        result = register_social_user(
            provider = 'google',
            email=data['access_token'].get('email'),
            first_name=data['access_token'].get('user'),
            last_name=data['access_token'].get('last_name')
        )
        return Response(result, status=status.HTTP_200_OK)

# delete a user’s question
class DeleteUserQuestion(DestroyAPIView):
    queryset = Question.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        question_id = kwargs.get('id')
        return super().delete(request, *args, **kwargs)
 
# update a question (only the owner can edit)
class QuestionUpdateView(RetrieveUpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)  # Restrict editing to question owner

    def perform_update(self, serializer):
        question_id = self.kwargs.get('id')
        closed_status = self.request.data.get('closed')
        if closed_status:
            serializer.save(closed = closed_status)
            return
        serializer.save()


#  accept or remove acceptance of an answer
class AcceptAnswerView(APIView):
    def post(self, request, question_id, answer_id):
        question = get_object_or_404(Question, id=question_id)
        answer = get_object_or_404(Answers, id=answer_id, question=question)

        accept = request.data.get('accept', None)

        if accept is None:
            return Response({"error": "'accept' field is required"}, status=status.HTTP_400_BAD_REQUEST)


        if question.user != request.user:
            return Response({"error":'you are not the owner of this question'}, status=status.HTTP_403_FORBIDDEN)

        if answer.user == question.user:
            return Response({"error": 'you cannot accept for your own question'}) 

        if question.accepted:
            if accept == False:
                answer.accepted = False
                question.accepted = False
                answer.save()
                question.save()
                return Response({"message":'answer acceptance is removed'}, status=status.HTTP_200_OK)
            else:
                return Response({"error": 'this question has already another accepted answer'})
        else:
            answer.accepted = True
            question.accepted = True
            answer.save()
            question.save() 
            return Response({"message": 'Answer acceptance status updated successfully'}, status=status.HTTP_200_OK)



