from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from .serializers import UserSerializer, ListUsersSeralizer
from .SocialSerializer.socialserializer import GoogleSignInSerializer
# from rest_framework import filters
# from rest_framework.filters import OrderingFilter
from .models import Users
from adminapp.models import Tag
from adminapp.serializer import TagSerializer

from .signal import generate_otp, send_otp_email

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.generics import ListAPIView

from QA.serializer import QuestionSerializer, AnswerSerializer
from QA.models import Question, Answers


class CreateUserView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data) 
        return super().create(request, *args, **kwargs)




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        if user.is_superuser:
            role = 'admin'
        else:
            role = 'user'

        token['role'] = role  
        token['is_verified'] = user.is_verified
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.is_superuser:
            role = 'admin'
        else:
            role = 'user'

        data['role'] = role  
        data['is_verified'] = self.user.is_verified
        
        return data


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

        send_otp_email(email, otp)

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

        send_otp_email(email, otp)
        print('otp succesfully avvandath ahnu')
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
        return Question.objects.filter(user=self.request.user)
    

class UserAnswerView(ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.filter(user=self.request.user)


class UserProfileUpdateView(RetrieveUpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        print(self.request.user)
        return self.request.user 
    
    def update(self, request, *args, **kwargs):
        print("Request data:", request.data)  # Print request data for debugging
        partial = kwargs.pop('partial', True)  # Allow partial updates
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

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = ((serializers.validated_data)['access_token'])
        return Response(data, status=status.HTTP_200_OK)


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