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


class CreateTaskView(APIView):
    def post(self,request:Request):
        data = request.data
        projectId = data.get('project')
        members_id = data.get('assigned_members')
        checked = data.get('checked')
        space_id = data.get('space_id')
        members = []
        for id in members_id:
            user = User.objects.get(**id)
            members.append(user)
        if projectId is None :
           
            project,created = Project.objects.get_or_create(name='Personal Tasks',status="In Progress",user=request.user)
            serializer = TaskSerializer(data=data)
            if serializer.is_valid():
                # workspace = WorkSpace.objects.get(owner=request.user,space_id=space_id)
                workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
                serializer.validated_data['workspace'] = workspace
                serializer.validated_data['status'] = "In Progress"
                serializer.validated_data['project'] = project
                task = serializer.save(user=request.user)
                user = User.objects.get(id=request.user.id)
                task.assigned_members.add(user)
                task.save()
                project.assigned_members.add(user)
                project.workspace = workspace
                project.save()
                return Response(data=serializer.data,status=status.HTTP_201_CREATED)
        else:
            serializer = TaskSerializer(data=data)
            if serializer.is_valid():
                # workspace = WorkSpace.objects.get(owner=request.user,space_id=space_id)
                workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
                serializer.validated_data['workspace'] = workspace
                serializer.validated_data['assigned_members'] = members
                serializer.validated_data['status'] = "In Progress"
                task = serializer.save(user=request.user)
                for user in members:
                    notification = Notification.objects.create(initiator=request.user,user=user,message=f'{request.user.username} assigned you to a task in the {task.project.name} project')
                    notification.save()
                if checked == True:
                    user = User.objects.get(id=request.user.id)
                    task.assigned_members.add(user)
                    task.save()
                return Response(data=serializer.data,status=status.HTTP_201_CREATED)    
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ListTaskView(APIView):
    def get(self, request:Request):
        space_id = request.query_params.get('space_id')
        workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
        task = Task.objects.filter(assigned_members = request.user,workspace=workspace)
        serializer = TaskSerializer(instance=task,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    
class AssignUsersToTask(APIView):
    def put(self,request:Request,pk):
        data = request.data
        newMembers = data.get("members")
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(instance=task,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            for user in newMembers:
                task.assigned_members.add(user)
                task.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)    

class SearchTaskMembers(APIView):
    def get(self,request:Request):
        search = request.query_params.get('search')
        task_id = request.query_params.get('task_id')
        project_id = request.query_params.get('project_id')
        workspace = WorkSpace.objects.get(owner=request.user,active=request.user)
        task = Task.objects.get(id=task_id)
        project = Project.objects.get(id=project_id)
        results = []
        for user in project.assigned_members.all():
            if user in task.assigned_members.all():
                pass
            else:
                if ".com" in search  or "@" in search or "gmail" in search:     
                    if search.lower() in str(user.email).lower():
                        if user not in results:
                            results.append(user)
                elif search.lower() in user.username.lower():
                    if user not in results:
                        results.append(user)
                elif search.lower() in user.first_name.lower():
                    if user not in results:
                        results.append(user)
                elif search.lower() in user.last_name.lower():
                    if user not in results:
                        results.append(user)
                else:
                    pass       
        serializer = UserSerializer(results,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)

class UpdateTask(APIView):
    def put(self,request:Request,pk):
        data = request.data
        task = Task.objects.get(id=pk)
        serializer = TaskSerializer(instance=task,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class DeleteTask(APIView):
    def delete(Self,request,pk):
        try:
            task= Task.objects.get(id=pk)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

class TodaysDueTaskView(APIView):
    def get(self,request:Request):
        space_id = request.query_params.get('space_id')
        dates =  date.today()
        workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
        task = Task.objects.filter(assigned_members=request.user,due_date=dates,workspace=workspace)[:5]
        serializer = TaskSerializer(instance=task,many=True)
        return Response(data=serializer.data,status=status.HTTP_200_OK)


class StatusOfTasks(APIView):
    def get(self,request:Request):
        space_id = request.query_params.get('space_id')
        workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[0]
        all_task = Task.objects.filter(assigned_members = request.user,workspace=workspace)
        completed_task = Task.objects.filter(assigned_members = request.user,status="Completed",workspace=workspace) 
        all_project = Project.objects.filter(assigned_members = request.user,workspace=workspace) 
        in_progress_task = Task.objects.filter(assigned_members = request.user,status="In Progress",workspace=workspace) 
        team = Team.objects.get(id=workspace.team.id)
        missed_deadline = []
        for task in all_task.all():
            if task.is_due() == True:
                missed_deadline.append(task)
            else:
                pass    
        today = timezone.now()
        range_days = 5
        start_date = today 
        end_date = today + timedelta(days=range_days)
        upcoming_deadlines = Task.objects.filter(due_date__range=(start_date,end_date),assigned_members = request.user,workspace=workspace).order_by("due_date")[:5]
        all_serializer = TaskSerializer(all_task,many=True)
        upcoming_deadlines_serializer = TaskSerializer(upcoming_deadlines,many=True)
        completed_serializer = TaskSerializer(completed_task,many=True)
        project_serializer = ProjectSerializer(all_project,many=True)
        in_progress_serializer = TaskSerializer(in_progress_task,many=True)
        missed_deadline_serializer = TaskSerializer(missed_deadline,many=True)
        team_serializer = TeamSerializer(team)
        response = {
            'all':all_serializer.data,
            'completed': completed_serializer.data,
            'projects':project_serializer.data,
            'in_progress':in_progress_serializer.data ,
            'upcoming':upcoming_deadlines_serializer.data,
            "team":team_serializer.data,
            "missed_deadline":missed_deadline_serializer.data,
        }
        return Response(data=response,status=status.HTTP_200_OK)
    

class CompleteTaskView(APIView):
    def put(self, request:Request,pk):
        data = request.data
        task = Task.objects.get(pk=pk)
        complete = data.get('complete')
        projectId = data.get('projectId')
        project = Project.objects.get(pk=projectId)
        serializer = TaskSerializer(instance=task,data=data,partial=True)
        if serializer.is_valid():
            if complete == True:
                serializer.validated_data['completed'] = True
                serializer.validated_data['status'] = 'Completed'
                task = serializer.save()
                for user in task.assigned_members.all():
                    if user == request.user:
                        notification = Notification.objects.create(initiator=request.user,user=user,message=f'You Completed a Task in the {project.name} Project')
                    else:
                        notification = Notification.objects.create(initiator=request.user,user=user,message=f'{request.user.username} Completed a Task in the {project.name} Project')    
                    notification.save()
                return Response(data=serializer.data,status=status.HTTP_200_OK)
            else:
                serializer.validated_data['completed'] = False
                serializer.validated_data['status'] = 'In Progress'
                serializer.save()
                return Response(data=serializer.data,status=status.HTTP_200_OK)            
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)
