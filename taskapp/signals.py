from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkSpace,Team
from accounts.models import User
import random

@receiver(post_save,sender=User)
def create_user_workspace(sender,instance,created,**kwargs):
    if created:
        space_id = random.randint(10001,99999)
        workspace = WorkSpace.objects.create(owner=instance,name=f"{instance.username}'s Workspace",space_id=space_id,main=True)
        workspace.active.add(instance)


@receiver(post_save,sender=WorkSpace)
def create_workspace(sender,instance,created,**kwargs):
    if created:
        user = User.objects.get(id=instance.owner.id)
        team = Team.objects.create(leader=user)
        team.members.add(instance.owner)
        team.save()
        # workspace = WorkSpace.objects.get(id=instance.id)
        # workspace.team = team
        # workspace.save()
        instance.team =team
        instance.save()
        
