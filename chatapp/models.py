from django.db import models
# from user.models import Users
from django.utils.timezone import now
from django.db import models

# Create your models here.


class Chat(models.Model):
    sender = models.ForeignKey('user.Users', on_delete=models.CASCADE, related_name="send_message")
    receiver = models.ForeignKey('user.Users', on_delete=models.CASCADE, related_name="receive_message")
    message = models.TextField(null=True)
    thread_name = models.CharField(max_length=255, null=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender.username} to {self.receiver.username} - {self.message[:30]} "
    
    class Meta:
        ordering = ['-date']




class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'Follow'),
        ('question', 'Question'),
        ('message', 'Message'),
        ('order_status', 'Order Status')
    )

    sender = models.ForeignKey('user.Users', on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey('user.Users', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=20)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.notification_type})"
