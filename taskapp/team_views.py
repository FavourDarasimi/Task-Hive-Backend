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


class TeamMembers(APIView):
    def get(self, request:Request):
        workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
        team = Team.objects.get(id=workspace.team.id)
        serializer = TeamSerializer(instance=team)            
        return Response(data=serializer.data,status=status.HTTP_200_OK)

class LeaveTeam(APIView):
    def put(self,request:Request,pk):
        data = request.data
        member_id = data.get('member_id')
        leader_id = data.get('leader_id')
        remove = data.get('remove')
        user = User.objects.get(id=member_id)
        leader = User.objects.get(id=leader_id)
        team = Team.objects.get(id=pk)
        serializer = TeamSerializer(instance=team,data=data,partial=True)
        workspace = WorkSpace.objects.get(team=team)
        
        if serializer.is_valid():
            updated_team = serializer.save()
            updated_team.members.remove(user)
            updated_team.save()
            projects = Project.objects.filter(workspace=workspace,assigned_members=user)
            for project in projects:
                tasks = Task.objects.filter(project=project,assigned_members=user)
                for task in tasks:
                    task.assigned_members.remove(user)
                    task.save()
                if project.user == user:
                    project.assigned_members.remove(user) 
                    project.user = leader
                    project.save()   
                else:     
                    project.assigned_members.remove(user) 
                    project.save()    
            if user in  workspace.active.all():
                workspace.active.remove(user)
                workspace.save()
                user_workspace = WorkSpace.objects.get(owner=user,main=True)
                user_workspace.active.add(user)
                user_workspace.save()
                if remove == False:
                    notification1 = Notification.objects.create(initiator=request.user,user=user,message=f'You left {workspace.name}')
                    notification2 = Notification.objects.create(initiator=request.user,user=leader,message=f'{user.username} left {workspace.name}')
                    notification1.save()
                    notification2.save()
                else:
                    notification1 = Notification.objects.create(initiator=request.user,user=user,message=f'{request.user.username} removed you from {workspace.name}')
                    notification2 = Notification.objects.create(initiator=request.user,user=leader,message=f'You removed {user.username} from {workspace.name}')
                    notification1.save()
                    notification2.save()    

            return Response(data=serializer.data,status=status.HTTP_200_OK)
        return Response(data = serializer.errors,status=status.HTTP_400_BAD_REQUEST)




class SendInvitationView(APIView):
    def post(self,request:Request):
        data = request.data
        email = data.get('email')
        space_id = data.get('space_id')
        workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()

        try:
            receiver = User.objects.get(email=email)
            try:
                team = Team.objects.get(members=receiver,id=workspace.team.id)
                try:
                    
                    team  = Team.objects.get(Q(leader=request.user) | Q(members=receiver),id=workspace.team.id)[0]
                    
                    response = {
                            'message':'User is in your team'
                        }
                    return Response(data=response,status=status.HTTP_200_OK)
                except Team.DoesNotExist:
                    response = {
                            'message':'User is in another team'
                        }
                    return Response(data=response,status=status.HTTP_200_OK)
                
            except Team.DoesNotExist:
                sender = request.user
                serializer = InvitationSerializer(data=data)
                if serializer.is_valid():
                    # workspace = WorkSpace.objects.get(owner=request.user,space_id=space_id)
                    workspace = WorkSpace.objects.filter(Q(owner=request.user) | Q(team__members = request.user),active=request.user)[:1].get()
                    serializer.validated_data['workspace'] = workspace
                    serializer.validated_data['sender'] = sender
                    serializer.validated_data['receiver'] = receiver
                    invite = serializer.save()
                    notification = Notification.objects.create(initiator=request.user,user=receiver,invite=invite,message=f'{sender.username} invited you to join his Team(Workspace)')
                    notification.save()
                    response = {
                        'message':'Invitation sent Successfully'
                    }
                return Response(data=response,status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            response = {
                'message':'User wih ths Email Address does not exist'
            } 
            return Response(data=response,status=status.HTTP_200_OK)

class ResponseToInvitationView(APIView):
    def put(self, request: Request,pk):
        data =request.data
        accepted = data.get('accepted')
        invitation = Invitation.objects.get(pk=pk)
        sender_id = data.get('sender')
        workspace_id = data.get('workspace')
        active_workspace_id = data.get('active')
        notification_id = data.get('notification_id')
        sender = User.objects.get(id=sender_id)
        workspace = WorkSpace.objects.get(id=workspace_id)  
        if accepted is True:
            serializer = InvitationSerializer(instance=invitation,data=data,partial=True)
            if serializer.is_valid():
                serializer.validated_data['responded'] = True
                serializer.validated_data['status'] = 'Accepted'
                serializer.save()
                      
                team = Team.objects.get(id=workspace.team.id)
                team.members.add(request.user)
                team.save()
                active_workspace = WorkSpace.objects.get(id=active_workspace_id)
                active_workspace.active.remove(request.user)
                active_workspace.save()
                workspace.active.add(request.user) 
                workspace.save()
                
                notification = Notification.objects.create(initiator=request.user,user=sender,message=f'{request.user.username} Accepted your invite')
                notification.save()
                new = Notification.objects.get(id=notification_id)
                new.message = f'You Accepted {sender.username} invite to join {workspace.name}'
                new.save()
                response = {
                    'accepted': 'You Accepted the invite'
                }
                return Response(data=response,status=status.HTTP_200_OK)
        else:
            serializer = InvitationSerializer(instance=invitation,data=data,partial=True)
            if serializer.is_valid():
                serializer.validated_data['responded'] = True
                serializer.validated_data['status'] = 'Declined'
                serializer.save()
                
                notification = Notification.objects.create(initiator=request.user,user=sender,message=f'{request.user.username} Rejected your invite')
                notification.save()
                new = Notification.objects.get(id=notification_id)
                new.message = f'You Rejected {sender.username} invite to join {workspace.name}'
                new.save()
            response = {
                'rejected':'You Rejected the Invite'
            }
            return Response(data=response,status=status.HTTP_200_OK, )
        
class UserInvitationView(APIView):
    def get(self, request:Request):
        invitations = Invitation.objects.filter(receiver=request.user).order_by("-sent_at")
        serializer = InvitationSerializer(invitations,many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)