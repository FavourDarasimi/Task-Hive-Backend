from django.contrib import admin
from .models import Task,Team,Project,Invitation,Notification,WorkSpace

class WorkSpaceAdmin(admin.ModelAdmin):
    list_display = ('name','owner','space_id',)
    search_fields = ('name',)
    
admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Invitation)
admin.site.register(Notification)
admin.site.register(WorkSpace,WorkSpaceAdmin)


# Register your models here.
