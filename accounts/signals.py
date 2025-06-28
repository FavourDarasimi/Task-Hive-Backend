from django.contrib.auth.signals import user_logged_in,user_logged_out
from django.db.models.signals import post_save
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.dispatch import receiver
from django.conf import settings
from .models import User,Profile


@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
       Profile.objects.create(user=instance)

@receiver(user_logged_in)
def user_logged_in_status(sender,request,user,**kwargs):
    user = User.objects.get(id=user.id)
    user.is_online = True
    user.save()

    
@receiver(user_logged_out)
def user_logged_out_status(sender,request,user,**kwargs):
    user = User.objects.get(id=user.id)
    user.is_online = False
    user.save()

@receiver(post_save,sender=Session)
def session_end_handle(sender,instance,**kwargs):
    if instance.expire_date < timezone.now():
        session_data = instance.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                user.is_online = False
                user.save()
            except User.DoesNotExist:
                pass       