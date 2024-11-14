from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from .serializers import *
from user.serializers import UserSerializer
from user.models import Users
from QA.models import *
from QA.serializer import *



# Create your views here.


class UserProfile(viewsets.ModelViewSet):
    """
        view set for managing user profile
    """
    
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        return Users.objects.filter(id = user.id)



class ChangePassword(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data = request.data , context = {'request':request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response({'detail': 'change password succesfull'}, status=status.HTTP_200_OK )
    


class UserQuestionView(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).order_by('-created')
    

class UserAnswerView(ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.filter(user=self.request.user)
    



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
    


class UserQuestionAnswerView(ListAPIView):
    serializer_class = AnswerSerializer
    def get_queryset(self):
        question_id = self.kwargs.get('id')
        return  Answers.objects.filter(question_id=question_id)



    

class FollowUserView(APIView):

    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_to_follow = Users.objects.get(id=user_id)
            request.user.follow(user_to_follow)
            return Response({"message": "followd successfully"}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({"error":"user does not found"}, status=status.HTTP_404_NOT_FOUND)


class UnfollowUserView(APIView):

    def post(self, request, user_id):
        try:
            user_to_unfollow = Users.objects.get(id=user_id)
            request.user.unfollow(user_to_unfollow)
            return Response({"message":"unfollowed successfully"}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({"error":"user does not found"}, status=status.HTTP_404_NOT_FOUND)
        

class FollowersListView(ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        try:
            user = Users.objects.get(id=self.kwargs['user_id'])
            return user.followers.all()
        except Users.DoesNotExist:
            raise NotFound(detail="User not found with the specified ID.")

    

class FollowingListView(ListAPIView):
    serializer_class = FollowingSerializer

    def get_queryset(self):
        try:
            user = Users.objects.get(id=self.kwargs['user_id'])
            return user.following.all()
        except Users.DoesNotExist:
            raise NotFound(detail='user not found with the specified ID')
        


class UserFollowCountsView(APIView):
    def get(self, request, username=None):
        if username:
            user = get_object_or_404(Users, username=username) 
        else:
            user = request.user
        data = {
            "follower_count": user.followers_count(),
            "following_count": user.following_count()
        }
        return Response(data, status=status.HTTP_200_OK)
    
    
class IsFollowingView(APIView):

    def get(self, request, username):
        try:
            target_user = Users.objects.get(username=username)
            is_following = request.user.is_following(target_user)
            return Response({"is_following": is_following}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    

class OtherUserProfile(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            print(user.username, args, kwargs, 'uuuuuuuuuuuussssr')
            if user.username == kwargs['username']:
                return Response({"detail":'Same user profile'})
            return self.retrieve(request, *args, **kwargs)
        except NotFound:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
