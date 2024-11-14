from django.db import models
from user.models import Users

# Create your models here.


class Chat(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="send_message")
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="receive_message")
    message = models.TextField(null=True)
    thread_name = models.CharField(max_length=255, null=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender.username} to {self.receiver.username} - {self.message[:30]} "
    
    class Meta:
        ordering = ['-date']