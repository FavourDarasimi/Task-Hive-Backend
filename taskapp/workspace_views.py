import random
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import TaskSerializer, TeamSerializer,ProjectSerializer,InvitationSerializer,NotificationSerializer,WorkSpaceSerializer
from accounts.serializers import ProfileSerializer, UserSerializer
from .models import Task,Team,Project,Invitation,Notification,WorkSpace
from accounts.models import Profile, User
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from datetime import datetime,date, timedelta
from django.db.models import Q
from django.conf import settings
from django.utils import timezone


class CreateWorkSpace(APIView):
    def post(self, request:Request):
        data = request.data
        serializer = WorkSpaceSerializer(data=data)
        if serializer.is_valid():
            serializer.validated_data['owner']=request.user
            space_id = random.randint(10001,99999)
            serializer.validated_data['space_id'] = space_id
            workspace = serializer.save()
            workspace.name = f"{workspace.name}'s Workspace"
            workspace.save()
            return Response(data=serializer.data,status=status.HTTP_201_CREATED)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class SwitchWorkspace(APIView):
    def post(self,request:Request):
        data = request.data
        last_workspace_id = data.get('last_workspace')        
        new_workspace_id = data.get('new_workspace')
        last_workspace = WorkSpace.objects.get(id=last_workspace_id)
        last_workspace.active.remove(request.user)
        last_workspace.save()
        new_workspace = WorkSpace.objects.get(id=new_workspace_id)
        new_workspace.active.add(request.user)
        new_workspace.save()
        response = {
            'message':'Workspace Switched Successfully'
        }
        return Response(data=response,status=status.HTTP_200_OK)

class UserWorkSpace(APIView):
    def get(self,request:Request):
        user_workspaces = WorkSpace.objects.filter(Q(owner=request.user)| Q(team__members=request.user)).distinct()
        active_workspace = WorkSpace.objects.filter(Q(owner=request.user)| Q(team__members=request.user),active = request.user)[0]
        user_workspaces_serializer = WorkSpaceSerializer(user_workspaces,many=True)
        active_workspace_serializer = WorkSpaceSerializer(active_workspace)
        response = {
            "workspaces":user_workspaces_serializer.data,
            "active":active_workspace_serializer.data,
        }
        return Response(data=response,status=status.HTTP_200_OK)