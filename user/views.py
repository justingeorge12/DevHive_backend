from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from .serializers import UserSerializer, ListUsersSeralizer, ChangePasswordSerializer, CustomTokenObtainPairSerializer
from .SocialSerializer.socialserializer import GoogleSignInSerializer
# from rest_framework import filters
# from rest_framework.filters import OrderingFilter
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












class CreateUserView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data) 
        return super().create(request, *args, **kwargs)






class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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



class OtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        typedOtp = request.data.get('otp')

        print(email, 'check email is typedddd................')
        print(email, typedOtp)

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
        

class getEmail(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        email = request.GET.get('email')
        user = Users.objects.filter(email=email, is_superuser = False).exists()
        if user:
            return Response(data='user exists', status=status.HTTP_200_OK)
        else:
            return Response(data='user is not exists', status=status.HTTP_404_NOT_FOUND)
        

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
    

class Logout(APIView):
    def post(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        

class ListUsers(ReadOnlyModelViewSet):
    queryset = Users.objects.filter(is_superuser = False).order_by('-total_votes')
    serializer_class = ListUsersSeralizer

    # ordering_fields = ['username', 'date_of_join', 'total_votes']



    # filter_backends = [filters.OrderingFilter]
    # ordering_fields = ['total_votes', 'username', 'location']  # Allow ordering by these fields
    # # ordering = ['-total_votes']  # Default ordering if no parameter is specified
  

class ListTags(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer



class UserProfile(viewsets.ModelViewSet):
    """
        view set for managing user profile
    """
    
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        return Users.objects.filter(id = user.id)
    


class UserQuestionView(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).order_by('-created')
    

class UserAnswerView(ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.filter(user=self.request.user)
    
# class UserSavedView(APIView):
#     def get(self, request):
#         user = self.request.user
#         saved_questions = SavedQuestion.objects.filter(user__id=user.id)
        
#         serializer = SavedQuestionSerializer(saved_questions, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class UserSavedView(ListAPIView):
    serializer_class = SavedQuestionSerializer

    def get_queryset(self):
        user = self.request.user
        return SavedQuestion.objects.filter(user_id=user.id)

class UserProfileUpdateView(RetrieveUpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user 
    
    def update(self, request, *args, **kwargs):
        print("Request data:", request.data) 
        partial = kwargs.pop('partial', True)  
        instance = self.get_object()
        if request.data.get('remove_image') == 'true':
            instance.profile.delete(save=False)
            instance.profile = None            

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data, status=status.HTTP_200_OK)



class GoogleSignInView(GenericAPIView):
    serializer_class=GoogleSignInSerializer
    permission_classes = [AllowAny]


    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)

        # data = ((serializers.validated_data)['access_token'])
        data = serializers.validated_data


        result = register_social_user(
            provider = 'google',
            email=data['access_token'].get('email'),
            first_name=data['access_token'].get('user'),
            last_name=data['access_token'].get('last_name')
        )
        return Response(result, status=status.HTTP_200_OK)




class ChangePassword(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data = request.data , context = {'request':request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response({'detail': 'change password succesfull'}, status=status.HTTP_200_OK )



class UserQuestionAnswerView(ListAPIView):
    serializer_class = AnswerSerializer
    def get_queryset(self):
        question_id = self.kwargs.get('id')
        return  Answers.objects.filter(question_id=question_id)



class DeleteUserQuestion(DestroyAPIView):
    queryset = Question.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        question_id = kwargs.get('id')
        return super().delete(request, *args, **kwargs)
 



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









# class HomeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         content = {'message': 'Welcome to jwt '}

#         return Response(content)

# class LogoutView(APIView):
#      permission_classes = (IsAuthenticated,)
#      def post(self, request):
          
#           try:
#                refresh_token = request.data["refresh_token"]
#                token = RefreshToken(refresh_token)
#                token.blacklist()
#                return Response(status=status.HTTP_205_RESET_CONTENT)
#           except Exception as e:
#                return Response(status=status.HTTP_400_BAD_REQUEST)