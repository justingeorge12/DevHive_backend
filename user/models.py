from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from userprofile.models import Follow
from chatapp.models import Notification

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self,email,username,password=None, **extra_fields):
        if not email:
            raise ValueError('The email feild must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        print('extra fields of create superuser',extra_fields)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        print(extra_fields)

        return self.create_user(email=email, username=username, password=password, **extra_fields)

AUTH_PROVIDERS = {'email':'email', 'google':'google', 'github':'github', 'facebook':'facebook'}

class Users(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=150, unique = True)
    bio = models.TextField(blank= True)
    profile = models.ImageField(upload_to='profile/', null= True, blank=True)
    skill = models.CharField(blank=True)
    phone = models.CharField(max_length=15, blank= True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    date_of_join = models.DateTimeField(auto_now_add=True, null=True)
    coins = models.IntegerField(default=0)
    location = models.CharField(null=True, blank= True)
    total_votes = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get("email"))

    def follow(self, user):
        if not self.is_following(user):
            Follow.objects.create(follower=self, following=user)

            Notification.objects.create(receiver = user, sender = self, message=f"{self.username} started following you.", notification_type='follow' )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                 f"user_{user.id}_notifications",{
                    "type": "send_notification",
                    "message": f"{self.username} started following you.",
                    # "type": "follow"
                 }
            )
            print(f"Message sent to group user_{user.id}_notifications")

    def unfollow(self, user):
        Follow.objects.filter(follower=self, following=user).delete()

    def is_following(self, user):
        return Follow.objects.filter(follower=self, following=user).exists()

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username",]


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )




    objects = CustomUserManager()


    def __str__(self):
        return f"{self.username} user instance"