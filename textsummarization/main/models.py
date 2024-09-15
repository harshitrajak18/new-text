from django.db import models
from django.contrib.auth.models import User

class userdata(models.Model):
     user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
     email=models.EmailField(max_length=255,unique=True)

     def __str__(self):
        return self.email


