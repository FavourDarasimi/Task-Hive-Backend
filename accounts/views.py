from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import render
from .serializers import SignUpSerializer,UserSerializer,ProfileSerializer
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.signals import user_logged_in,user_logged_out
from rest_framework.permissions import IsAuthenticated
from .models import User,Profile



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self,attrs):
        data = super().validate(attrs)
        user = self.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        user_logged_in.send(sender=user.__class__,request=self.context['request'],user=user)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request):
        user = request.user
        logout(request)
        user_logged_out.send(sender=user.__class__,request=request,user=user)
        return Response(data='User logged out',status=status.HTTP_200_OK)


class SignUpView(APIView):
    serializer_class = SignUpSerializer

    def post(self,request:Request):
        data = request.data
        serializer = SignUpSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'message':'User Created Successfully',
                'data': serializer.data
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class UserIsAutheticated(APIView):
    def get(self,request:Request):
        if request.user.is_authenticated:
            user = UserSerializer(request.user)
            return Response(data={'is_authenticated':True,'user':user.data},status=status.HTTP_200_OK)
        else:
            return Response({'is_authenticated':False},status=status.HTTP_200_OK)
        
class UpdateProfile(APIView):
    def put(self,request:Request):
        profile = Profile.objects.get(user=request.user)    
        data=request.data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        user = User.objects.get(id=request.user.id)
        serializer = ProfileSerializer(instance=profile,data=data,partial=True)
        if serializer.is_valid():
            print(first_name)
            serializer.save()
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:    
                user.last_name = last_name
            if email is not None:
                user.email = email
            user.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)    
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)                  

class ProfileView(APIView):
    def get(Self,request:Request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(data=serializer.data,status=status.HTTP_200_OK)  
# Create your views here.
