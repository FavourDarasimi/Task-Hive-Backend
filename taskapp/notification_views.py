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



class NotificationView(APIView):
    def get(self,request:Request):
        notification = Notification.objects.filter(user=request.user).order_by("-date_created")
        serializer = NotificationSerializer(notification,many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
class UnReadNotificationView(APIView):
    def get(self,request:Request):        
        notification = Notification.objects.filter(user=request.user,read=False).order_by("-date_created")
        serializer = NotificationSerializer(notification,many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)   

class MarkAsReadView(APIView):
    def put(self, request:Request,pk):
        
        data = request.data
        notification = Notification.objects.get(pk=pk)
        serializer = NotificationSerializer(instance=notification,data=data,partial=True)
        if serializer.is_valid():
            serializer.validated_data['read'] = True
            serializer.save()
            response = {
            'Message':'Notification Read'
            }
            return Response(data=response,status=status.HTTP_200_OK, )   
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class MarkAllAsReadView(APIView):
    def post(self, request:Request):
        notifications = Notification.objects.filter(user=request.user,read=False)
        for notification in notifications:
            notification.read = True
            notification.save()
        response = {
            'Read':'All Notification Read'
        }
        return Response(data=response,status=status.HTTP_200_OK)