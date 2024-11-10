from django.db import models

# Create your models here.



class Follow(models.Model):
    follower = models.ForeignKey("user.Users", related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey("user.Users", related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('follower', 'following')


    def __str__(self):
        return f"{self.follower} follows {self.following}"