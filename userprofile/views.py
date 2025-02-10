from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView
from .serializers import *
from user.serializers import UserSerializer
from user.models import Users
from QA.models import *
from QA.serializer import *
from rewards.models import Address
from rewards.serializers import UserAddressSerializer
from rest_framework import filters



# view set for managing user profile
class UserProfile(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        return Users.objects.filter(id = user.id)


# to  change the user password
class ChangePassword(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data = request.data , context = {'request':request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response({'detail': 'change password succesfull'}, status=status.HTTP_200_OK )
    

# retirves the question ansked by the current user
class UserQuestionView(ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).order_by('-created')
    
# retirves the answer don by the current user
class UserAnswerView(ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.filter(user=self.request.user).order_by('-id')
    

# retrive list of saved questions
class UserSavedView(ListAPIView):
    serializer_class = SavedQuestionSerializer

    def get_queryset(self):
        user = self.request.user
        return SavedQuestion.objects.filter(user_id=user.id)
    
# to update user profile
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
    

# retrive all answers for a given question
class UserQuestionAnswerView(ListAPIView):
    serializer_class = AnswerSerializer
    def get_queryset(self):
        question_id = self.kwargs.get('id')
        return  Answers.objects.filter(question_id=question_id)

# user to update or delete their own answers
class UserAnswerDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answers.objects.filter(user = self.request.user)
    
    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have the permission to view this")
        return obj
    
    def perform_update(self, serializer):
        answer = self.get_object()
        if answer.user != self.request.user:
            raise PermissionDenied("you are not allowed to edit the answer")
        
        if set(serializer.validated_data.keys()) != {'body'}:
            raise PermissionDenied("You can only update the body field.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You are not allowed to delete the answer")
        if instance.accepted == True:
            raise PermissionDenied("You cannot delete a accepted answer")
        if instance.pos_vote > 0:
            raise PermissionDenied("You cannot delete a answer which has positive votes")
        
        instance.delete()
    
# user to follow another user
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

# user to unfollow another user
class UnfollowUserView(APIView):

    def post(self, request, user_id):
        try:
            user_to_unfollow = Users.objects.get(id=user_id)
            request.user.unfollow(user_to_unfollow)
            return Response({"message":"unfollowed successfully"}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({"error":"user does not found"}, status=status.HTTP_404_NOT_FOUND)
        
# Retrieves a list of users following a specific user
class FollowersListView(ListAPIView):
    serializer_class = FollowerSerializer

    def get_queryset(self):
        try:
            user = Users.objects.get(id=self.kwargs['user_id'])
            return user.followers.all()
        except Users.DoesNotExist:
            raise NotFound(detail="User not found with the specified ID.")

    
# Retrieves a list of users that a specific user is following
class FollowingListView(ListAPIView):
    serializer_class = FollowingSerializer

    def get_queryset(self):
        try:
            user = Users.objects.get(id=self.kwargs['user_id'])
            return user.following.all()
        except Users.DoesNotExist:
            raise NotFound(detail='user not found with the specified ID')
        

#  Retrieves the follower and following count of a user
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
    
# Checks if the logged-in user is following another user
class IsFollowingView(APIView):

    def get(self, request, username):
        try:
            target_user = Users.objects.get(username=username)
            is_following = request.user.is_following(target_user)
            return Response({"is_following": is_following}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    
# Retrieves another user's profile based on username
class OtherUserProfile(generics.RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            if user.username == kwargs['username']:
                return Response({"detail":'Same user profile'})
            return self.retrieve(request, *args, **kwargs)
        except NotFound:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            

# Allows a user to retrieve or update their address
class AddressRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Address.objects.all()
    serializer_class = UserAddressSerializer
    lookup_field = "id" 

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    


# Searches for other users based on username or first name
class SeachOtherUser(ListAPIView):
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name']


    def get_queryset(self):
        requested_user = self.request.user
        queryset = Users.objects.exclude(id=requested_user.id).exclude(is_superuser=True)

        search_param = self.request.query_params.get('search', None)
        if search_param:
            queryset = queryset.filter(username__istartswith=search_param) | queryset.filter(first_name__istartswith=search_param)

        return queryset