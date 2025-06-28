from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_online = models.BooleanField(default=False,blank=True)

    def __str__(self) -> str:
        return self.username
    

class Profile(models.Model):
    user = models.OneToOneField(User,blank=True,on_delete=models.CASCADE)
    age = models.PositiveIntegerField(blank=True,null=True)
    avatar = models.ImageField(blank=True,null=True,upload_to='images/')
    phone_number = models.PositiveIntegerField(blank=True,null=True)
    gender = models.CharField(blank=True,null=True,max_length=100)
    occupation = models.CharField(blank=True,null=True,max_length=100)

    def __str__(self):
        return self.user.username


# Create your models here.
