from django.db import models
from adminapp.models import Tag
from user.models import Users

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chatapp.models import Notification
# Create your models here.


class QuestionTag(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='questions')

class Question(models.Model):
    title = models.CharField(max_length=400, unique=True)
    body = models.TextField()
    pos_vote = models.IntegerField(default=0)
    neg_vote = models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    answer_count = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag, through=QuestionTag)


    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        super().save(*args, **kwargs)
        if is_new:
            self.notify_followers()

    def notify_followers(self):
        followers = self.user.followers.all()
        channel_layer = get_channel_layer()

        for follower in followers:
            Notification.objects.create(
                receiver=follower.follower, 
                sender=self.user,
                message=f"{self.user.username} asked a new question: {self.title}",
                notification_type='question'
            )
            
            async_to_sync(channel_layer.group_send)(
                f"user_{follower.follower.id}_notifications",
                {
                    "type": "send_notification",
                    "message": f"{self.user.username} asked a new question: {self.title}",
                }
            )
    

class Answers(models.Model):
    body = models.TextField()
    pos_vote = models.IntegerField(default=0)
    neg_vote = models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class QuestionVotes(models.Model):
    UPVOTE = 'upvote'
    DOWNVOTE = 'downvote'
    NONE = 'none'

    VOTE_CHOICES = [
        (UPVOTE, 'Upvote'),(DOWNVOTE, 'Downvote'),(NONE, 'None'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    vote_type = models.CharField( max_length=10, choices=VOTE_CHOICES, default=NONE)


class SavedQuestion(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class AnswerVotes(models.Model):
    UPVOTE = 'upvote'
    DOWNVOTE = 'downvote'
    NONE = 'none'

    VOTE_CHOICES = [
        (UPVOTE, 'Upvote'),(DOWNVOTE, 'Downvote'),(NONE, 'None'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE)
    vote_type = models.CharField( max_length=10, choices=VOTE_CHOICES, default=NONE)



class SavedAnswer(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
