from datetime import date, timedelta
from django.utils import timezone
import math
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL
# Create your models here.

Priority = {
    'High':'High',
    'Medium':'Medium',
    'Low':'Low',
}

Status = {
    'Completed':'Completed',
    'In Progress':'In Progress'
}

InvtationStatus = {
    'Accepted':'Accepted',
    'Declined':'Declined'
}


    


class Team(models.Model):
    leader = models.ForeignKey(User,on_delete=models.CASCADE,related_name='team_leader')
    members = models.ManyToManyField(User)

    def __str__(self):
        return str(self.leader)
    
    def __save__(self,*args, **kwargs):
        super().save(*args, **kwargs)
        self.members.add(self.leader)

class WorkSpace(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,blank=True)
    space_id = models.PositiveIntegerField(null=True,blank=True)
    active = models.ManyToManyField(User,related_name="active",blank=True)
    team = models.OneToOneField(Team, on_delete=models.CASCADE, blank=True,null=True)
    main = models.BooleanField(default=False, null=True,blank=True)     

    def __str__(self):
        return f"{self.name}-{self.id}"   


class Project(models.Model):
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True)
    name = models.CharField(max_length=100)
    assigned_members = models.ManyToManyField(User,related_name='project_members',blank=True)
    status = models.CharField(choices=Status,max_length=50, blank=True)
    created_at = models.DateField(auto_now=True)
    favourite = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}-{str(self.user)}'
    

class Task(models.Model):
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True)
    title = models.CharField(max_length=300)
    created_at = models.DateField(auto_now=True)
    due_date = models.DateField()
    priority = models.CharField(choices=Priority,max_length=50)
    status = models.CharField(choices=Status,max_length=50, blank=True)
    assigned_members = models.ManyToManyField(User,related_name='assigned_members',blank=True)
    completed = models.BooleanField(default=False)
    project = models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True )

    def __str__(self):
        return f'{self.title} - {str(self.user)} - {self.project.name}'
    
    def __save__(self,*args, **kwargs):
        super().save(*args, **kwargs)
        self.assigned_members.add(self.user)

    def is_due(self):
        due = self.due_date < date.today()
        not_complete = self.status != 'Completed'
        return due & not_complete    
   



class Invitation(models.Model):
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE,null=True,blank=True)
    sender = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="sender")
    receiver = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="receiver")
    responded = models.BooleanField(default=False)
    status = models.CharField(choices=InvtationStatus,max_length=50,blank=True,null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username}"
    
    def time_since_created(self):
        now=timezone.now()
        diff = now - self.sent_at
        if diff.days ==0 and diff.seconds <60:
            return f'{diff.seconds} seconds ago'
        elif diff.days == 0 and diff.seconds<3600:
            minutes = math.floor(diff.seconds/60)
            return f'{minutes} minutes ago'
        elif diff.days == 0:
            hours = math.floor(diff.seconds/3600)
            if hours==1:
                return f'{hours} hour ago'
            else:
                return f'{hours} hours ago'
            
        elif diff.days < 30:
            if diff.days == 1:
                return f'{diff.days} day ago'
            else:
                return f'{diff.days} days ago'
        elif diff.days < 365:
            month = math.floor(diff.days/30)
            return  f'{month} months ago'
        else:
            years = math.floor(diff.days/365)
            return f'{years} years ago'

class Notification(models.Model):
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE,null=True,blank=True)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name="initiator")
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    message  = models.CharField(max_length=100)
    read =  models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    starred = models.BooleanField(default=False)
    invite = models.ForeignKey(Invitation,on_delete=models.DO_NOTHING,null=True,blank=True)

    def __str__(self):
        return self.user.username
    