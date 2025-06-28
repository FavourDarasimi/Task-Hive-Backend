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

class CreateProjectView(APIView):
    def post(self, request:Request):
        data = request.data
        members_id = data.get('assigned_members')
        # space_id = data.get('space_id')
        members = []
        for id in members_id:
            user = User.objects.get(**id)
            members.append(user)
        
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            # workspace = WorkSpace.objects.get(owner=request.user,space_id=space_id)
            workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
            serializer.validated_data['workspace'] = workspace
            serializer.validated_data['assigned_members'] = members
            serializer.validated_data['status'] = "In Progress"    
            project = serializer.save(user=request.user)
            notification = Notification.objects.create(initiator=request.user,user=request.user,message=f'You Created {project.name} Project')
            notification.save()
            for user in members:
                notification = Notification.objects.create(initiator=request.user,user=user,message=f'{request.user.username} assigned you to a {project.name} Project')
                notification.save()
            user = User.objects.get(id=request.user.id)
            project.assigned_members.add(request.user)
            project.save()
            return Response(data=serializer.data,status=status.HTTP_201_CREATED)
              
            
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ListProjectView(APIView):
    def get(self,request:Request):
        # space_id = request.query_params.get('space_id')
        workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
        try:
            team = Team.objects.get(members=request.user,workspace=workspace)
            workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
            projects = Project.objects.filter( Q(assigned_members=request.user) | Q(user=request.user),workspace= workspace).distinct()      
            serializer = ProjectSerializer(projects,many=True) 
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            projects = Project.objects.filter( user=request.user,workspace= workspace ).distinct()
            serializer = ProjectSerializer(projects,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)

class AddUserToProject(APIView):
    def put(self,request:Request,pk):
        data = request.data
        name= data.get('param')
        project = Project.objects.get(id=pk)
        serializer = ProjectSerializer(instance=project,data=data,partial=True)
        if serializer.is_valid():
            updated_project = serializer.save()
            try:
                user = User.objects.get(Q(username=name) | Q(email=name))
                try:
                    workspace = WorkSpace.objects.get(id=project.workspace.id)
                    team = Team.objects.get(id=workspace.team.id,members=user)
                    if user in project.assigned_members.all():
                        response = {
                            'message':'User Already Added'
                        }  
                    else:
                        updated_project.assigned_members.add(user)
                        updated_project.save()
                        response = {
                            'message':'User Added'
                        }
                         
                except Team.DoesNotExist:
                    response = {
                        'message':'User not in your Team'
                    }
            except User.DoesNotExist:
                if ".com" in name  or "@" in name or "gmail" in name:
                    response = {
                        'message':'User with this email address does not exist'
                    }
                else:
                    response = {
                        'message':'User with this Username does not exist'
                    }        
                
            return Response(data=response,status=status.HTTP_200_OK)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class RemoveUserFromProject(APIView):
    def put(self,request:Request,pk):
        data = request.data
        name= data.get('param')
        project = Project.objects.get(id=pk)
        serializer = ProjectSerializer(instance=project,data=data,partial=True)
        if serializer.is_valid():
            updated_project = serializer.save()
            try:
                user = User.objects.get(Q(username=name) | Q(email=name))
                try:
                    workspace = WorkSpace.objects.get(id=project.workspace.id)
                    team = Team.objects.get(id=workspace.team.id,members=user)
                    if user in project.assigned_members.all():
                        if user == project.user:
                            response = {
                            'message':"You can't remove the creator of the project"
                        }
                        else:
                            tasks = Task.objects.filter(project=project,assigned_members=user)
                            for task in tasks:
                                task.assigned_members.remove(user)
                                task.save()    
                            updated_project.assigned_members.remove(user)
                            updated_project.save()
                            response = {
                                'message':'User Removed'
                            }
                    else:
                        response = {
                            'message':"User Not Assigned To this Project"
                        }    
                except Team.DoesNotExist:
                    response = {
                        'message':'User not in your Team'
                    }
            except User.DoesNotExist:
                if ".com" in name  or "@" in name or "gmail" in name:
                    response = {
                        'message':'User with this email address does not exist'
                    }
                else:
                    response = {
                        'message':'User with this Username does not exist'
                    }        
                
            return Response(data=response,status=status.HTTP_200_OK)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class UpdateProject(APIView):
    def put(self,request:Request,pk):
        data = request.data
        project = Project.objects.get(id=pk)
        serializer = ProjectSerializer(instance=project,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class DetailProjectView(APIView):
    def get(self,request:Request,pk):
        project = Project.objects.get(pk=pk)
        task = Task.objects.filter(project=project)
        taskSerializer = TaskSerializer(task,many=True)
        projectSerializer = ProjectSerializer(project)
        response = {
            'project':projectSerializer.data,
            'task':taskSerializer.data
        }
        return Response(data=response,status=status.HTTP_200_OK)

class ProjectTaskDueToday(APIView):
    def get(self,request:Request,pk):
        project = Project.objects.get(pk=pk)
        dates =  date.today()
        task = Task.objects.filter(project=project,due_date=dates,completed=False)
        serializer = TaskSerializer(task,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)

class DeleteProject(APIView):
    def delete(Self,request,pk):
        try:
            project= Project.objects.get(id=pk)
            tasks = Task.objects.filter(project=project)
            for task in tasks:
                task.delete()
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

class SearchResult(APIView):
    def get(self,request:Request):
        search = request.query_params.get('search')
        workspace = WorkSpace.objects.get(active=request.user)
        projects = Project.objects.filter(assigned_members=request.user,workspace=workspace)
        results = []
        for project in projects:
            if search.lower() in project.name.lower():
                results.append(project)
            else:
                pass 
        serializer = ProjectSerializer(results,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)

class AddProjectToFavorites(APIView):
    def put(self,request:Request,pk):
        data = request.data
        fav = data.get("favourite")
        project = Project.objects.get(pk=pk)
        serializer = ProjectSerializer(instance=project,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            project.favourite = fav
            project.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK, )   
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)