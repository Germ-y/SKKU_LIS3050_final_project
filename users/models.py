from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    INTEREST_CHOICES = [
        ('econ', '경제학'),
        ('cs', '컴퓨터과학'),
        ('math', '수학'),
        ('stat', '통계학'),
        ('physics', '물리학'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interest = models.CharField(max_length=10, choices=INTEREST_CHOICES, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()